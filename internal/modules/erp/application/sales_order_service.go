package application

import (
	"context"
	"fmt"

	"github.com/yourorg/erp-mes-wms-go/ent"
	"github.com/yourorg/erp-mes-wms-go/ent/salesorder"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/domain/dto"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/domain/valobj"
	"go.uber.org/zap"
	"entgo.io/ent/dialect/sql"
)

// SalesOrderService handles ERP sales order business logic
type SalesOrderService struct {
	db  *ent.Client
	log *zap.Logger
}

// NewSalesOrderService creates a new SalesOrderService
func NewSalesOrderService(db *ent.Client, log *zap.Logger) *SalesOrderService {
	return &SalesOrderService{db: db, log: log}
}

// CreateOrder creates a sales order and its items within an Ent transaction.
func (s *SalesOrderService) CreateOrder(ctx context.Context, req *dto.CreateSalesOrderReq) (*ent.SalesOrder, error) {
	// Start transaction
	tx, err := s.db.Tx(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to start transaction: %w", err)
	}
	// Use standard idiomatic rollback which safely acts as a no-op if committed, 
	// while guaranteeing rollback on error paths or panics.
	defer tx.Rollback()

	s.log.Info("Creating SalesOrder", zap.String("order_number", req.OrderNumber))

	// Calculate total amount
	var totalAmount float64
	for _, item := range req.Items {
		totalAmount += item.Quantity * item.UnitPrice
	}

	// 1. Create the Order header (Aggregate Root)
	order, err := tx.SalesOrder.Create().
		SetOrderNumber(req.OrderNumber).
		SetClientName(req.ClientName).
		SetTotalAmount(totalAmount).
		SetState(string(valobj.StateDraft)).
		Save(ctx)

	if err != nil {
		return nil, fmt.Errorf("failed to create order header: %w", err)
	}

	// 2. Prepare items for bulk insert
	itemCreates := make([]*ent.SalesOrderItemCreate, len(req.Items))
	for i, itemReq := range req.Items {
		itemCreates[i] = tx.SalesOrderItem.Create().
			SetQuantity(itemReq.Quantity).
			SetUnitPrice(itemReq.UnitPrice).
			SetOrder(order).
			SetMaterialID(itemReq.MaterialID)
	}

	// 3. Execute bulk insert
	_, err = tx.SalesOrderItem.CreateBulk(itemCreates...).Save(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to create order items: %w", err)
	}

	// Commit transaction
	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	return order, nil
}

// ApproveOrder approves an order, subject to state machine transition rules.
func (s *SalesOrderService) ApproveOrder(ctx context.Context, orderID int) error {
	// Start transaction for atomicity (could be just an UpdateOne, but we might do more here later)
	tx, err := s.db.Tx(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	order, err := tx.SalesOrder.Query().
		Where(salesorder.ID(orderID)).
		Modify(func(s *sql.Selector) {
			s.ForUpdate()
		}).
		Only(ctx)

	if err != nil {
		return fmt.Errorf("failed to query order: %w", err)
	}

	// Check State Machine Rule
	currentState := valobj.OrderState(order.State)
	// For approval, it must be PendingApproval.
	// Note: in a real workflow, someone might submit draft to pending first. 
	// For simplicity, let's assume we allow Draft -> Pending -> Approved here, or just PENDING_APPROVAL.
	// But let's strictly use the state machine. 
	// If it's DRAFT, we can't directly approve it unless we transition it. 
	// Let's assume the user directly approves it: from DRAFT to PENDING is needed first.
	// To make this endpoint useful, let's allow PENDING_APPROVAL -> APPROVED.
	if !valobj.CanTransition(currentState, valobj.StateApproved) {
		return valobj.ErrInvalidStateTransition
	}

	_, err = tx.SalesOrder.UpdateOne(order).
		SetState(string(valobj.StateApproved)).
		Save(ctx)

	if err != nil {
		return fmt.Errorf("failed to update order state: %w", err)
	}

	return tx.Commit()
}

// GetOrder fetches a sales order and preloads its items and their materials.
func (s *SalesOrderService) GetOrder(ctx context.Context, orderID int) (*dto.OrderResp, error) {
	order, err := s.db.SalesOrder.Query().
		Where(salesorder.ID(orderID)).
		WithItems(func(q *ent.SalesOrderItemQuery) {
			q.WithMaterial() // Eager load the material for each item
		}).
		Only(ctx)

	if err != nil {
		return nil, fmt.Errorf("failed to query order: %w", err)
	}

	resp := &dto.OrderResp{
		ID:          order.ID,
		OrderNumber: order.OrderNumber,
		ClientName:  order.ClientName,
		TotalAmount: order.TotalAmount,
		State:       order.State,
		Items:       make([]dto.OrderItemResp, len(order.Edges.Items)),
	}

	for i, item := range order.Edges.Items {
		resp.Items[i] = dto.OrderItemResp{
			ID:           item.ID,
			Quantity:     item.Quantity,
			UnitPrice:    item.UnitPrice,
		}
		if item.Edges.Material != nil {
			resp.Items[i].MaterialCode = item.Edges.Material.MaterialCode
			resp.Items[i].MaterialName = item.Edges.Material.Name
		}
	}

	return resp, nil
}
