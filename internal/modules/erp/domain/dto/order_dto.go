package dto

// OrderItemReq represents an item within a sales order request
type OrderItemReq struct {
	MaterialID int     `json:"material_id" binding:"required"`
	Quantity   float64 `json:"quantity" binding:"required,gt=0"`
	UnitPrice  float64 `json:"unit_price" binding:"required,gte=0"`
}

// CreateSalesOrderReq represents the request body for creating a sales order
type CreateSalesOrderReq struct {
	OrderNumber string         `json:"order_number" binding:"required"`
	ClientName  string         `json:"client_name" binding:"required"`
	Items       []OrderItemReq `json:"items" binding:"required,min=1"`
}

// OrderResp represents the response body for a sales order
type OrderResp struct {
	ID          int             `json:"id"`
	OrderNumber string          `json:"order_number"`
	ClientName  string          `json:"client_name"`
	TotalAmount float64         `json:"total_amount"`
	State       string          `json:"state"`
	Items       []OrderItemResp `json:"items,omitempty"`
}

// OrderItemResp represents the response for an order item
type OrderItemResp struct {
	ID           int     `json:"id"`
	MaterialCode string  `json:"material_code"`
	MaterialName string  `json:"material_name"`
	Quantity     float64 `json:"quantity"`
	UnitPrice    float64 `json:"unit_price"`
}
