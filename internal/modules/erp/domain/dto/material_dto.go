package dto

import "errors"

var (
	ErrMaterialNotFound = errors.New("material not found")
	ErrBOMCycleDetected = errors.New("BOM cycle detected: cannot add ancestor as a child")
)

// CreateMaterialReq represents the request body for creating a material
type CreateMaterialReq struct {
	MaterialCode   string `json:"material_code" binding:"required"`
	Name           string `json:"name" binding:"required"`
	Type           string `json:"type" binding:"required,oneof=raw semi finished"`
	Specifications string `json:"specifications"`
}

// AddBOMReq represents the request body for adding a BOM component
type AddBOMReq struct {
	ChildID  int   `json:"child_id" binding:"required"`
	// For simplicity in the initial schema we didn't add quantity to the material self-referencing edge,
	// but normally it would be an edge property or an associative entity.
	// We'll accept it here to match the spec.
	Quantity float64 `json:"quantity" binding:"required,gt=0"`
}

// BOMNodeResp represents a node in the BOM tree structure
type BOMNodeResp struct {
	ID             int            `json:"id"`
	MaterialCode   string         `json:"material_code"`
	Name           string         `json:"name"`
	Type           string         `json:"type"`
	Specifications string         `json:"specifications"`
	Children       []*BOMNodeResp `json:"children,omitempty"`
}
