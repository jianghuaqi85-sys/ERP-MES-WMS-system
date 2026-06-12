package dto

// DeductStockReq represents the request to deduct stock
type DeductStockReq struct {
	MaterialID int     `json:"material_id" binding:"required"`
	Quantity   float64 `json:"quantity" binding:"required,gt=0"`
	OrderID    *int    `json:"order_id,omitempty"` // Reference SalesOrder or WorkOrder
}
