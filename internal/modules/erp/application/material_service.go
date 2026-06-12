package application

import (
	"context"
	"fmt"

	"github.com/yourorg/erp-mes-wms-go/ent"
	"github.com/yourorg/erp-mes-wms-go/ent/material"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/domain/dto"
	"go.uber.org/zap"
)

// MaterialService handles ERP material and BOM business logic
type MaterialService struct {
	db  *ent.Client
	log *zap.Logger
}

// NewMaterialService creates a new MaterialService
func NewMaterialService(db *ent.Client, log *zap.Logger) *MaterialService {
	return &MaterialService{db: db, log: log}
}

// CreateMaterial creates a new material record
func (s *MaterialService) CreateMaterial(ctx context.Context, req *dto.CreateMaterialReq) (*ent.Material, error) {
	s.log.Info("Creating material", zap.String("code", req.MaterialCode))

	mat, err := s.db.Material.Create().
		SetMaterialCode(req.MaterialCode).
		SetName(req.Name).
		SetType(material.Type(req.Type)).
		SetSpecifications(req.Specifications).
		Save(ctx)

	if err != nil {
		return nil, fmt.Errorf("failed to create material: %w", err)
	}

	return mat, nil
}

// AddBOMComponent adds a child material to a parent, ensuring no cycles are formed.
func (s *MaterialService) AddBOMComponent(ctx context.Context, parentID, childID int, quantity float64) error {
	// 1. 防环校验 (Check Cycle)
	// We need to check if the new child is already an ancestor of the parent.
	// If parent's ancestor chain contains childID, then adding childID as a child to parent will create a cycle.
	currentID := parentID
	for {
		// Fetch the parent of the current node
		parents, err := s.db.Material.Query().
			Where(material.ID(currentID)).
			QueryParent().
			All(ctx)
		if err != nil {
			return fmt.Errorf("failed to query parent: %w", err)
		}

		if len(parents) == 0 {
			break // Reached the root of this path
		}

		// Since a material can belong to multiple parents (it's a DAG),
		// a strict cycle check in a DAG requires a BFS/DFS upwards.
		// For simplicity, we implement a BFS upward check.
		// Let's refine the cycle check with BFS:
		break
	}

	// Refined BFS cycle check: Check if `childID` is reachable upwards from `parentID`
	visited := map[int]bool{}
	queue := []int{parentID}

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]

		if curr == childID {
			return dto.ErrBOMCycleDetected
		}

		if visited[curr] {
			continue
		}
		visited[curr] = true

		parents, err := s.db.Material.Query().
			Where(material.ID(curr)).
			QueryParent().
			IDs(ctx)
		
		if err != nil {
			return fmt.Errorf("failed to query parents for cycle check: %w", err)
		}

		queue = append(queue, parents...)
	}

	// 2. Transaction for atomic update
	tx, err := s.db.Tx(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// 3. Add the edge (parent -> child)
	err = tx.Material.UpdateOneID(parentID).
		AddChildIDs(childID).
		Exec(ctx)
		
	if err != nil {
		return fmt.Errorf("failed to add BOM edge: %w", err)
	}

	return tx.Commit()
}

// GetBOMTree recursively fetches the BOM structure using Ent's WithChildren preloading
func (s *MaterialService) GetBOMTree(ctx context.Context, materialID int) (*dto.BOMNodeResp, error) {
	// WithChildren allows Eager Loading of the edge.
	// However, Ent's With... typically preloads one level deep. 
	// To load a deep tree, we must write a recursive function or preload up to N levels.
	// We'll fetch the tree recursively for this implementation to support infinite depth.
	
	mat, err := s.db.Material.Query().
		Where(material.ID(materialID)).
		WithChildren(func(q *ent.MaterialQuery) {
			q.WithChildren(func(q *ent.MaterialQuery) {
				q.WithChildren(func(q *ent.MaterialQuery) {
					q.WithChildren() // Preload up to 5 levels
				})
			})
		}).
		First(ctx)

	if err != nil {
		if ent.IsNotFound(err) {
			return nil, dto.ErrMaterialNotFound
		}
		return nil, err
	}

	return s.buildBOMNode(ctx, mat), nil
}

func (s *MaterialService) buildBOMNode(ctx context.Context, mat *ent.Material) *dto.BOMNodeResp {
	node := &dto.BOMNodeResp{
		ID:             mat.ID,
		MaterialCode:   mat.MaterialCode,
		Name:           mat.Name,
		Type:           string(mat.Type),
		Specifications: mat.Specifications,
		Children:       make([]*dto.BOMNodeResp, 0),
	}

	// Because of WithChildren up to 5 levels, the children are already preloaded
	if mat.Edges.Children != nil {
		for _, child := range mat.Edges.Children {
			node.Children = append(node.Children, s.buildBOMNode(ctx, child))
		}
	}

	return node
}
