package dto

// ReportProductionReq represents the request for production reporting (报工)
type ReportProductionReq struct {
	WorkerID string  `json:"worker_id" binding:"required"`
	Quantity float64 `json:"quantity" binding:"required,gt=0"`
	Barcode  string  `json:"barcode" binding:"required"` // Unique barcode for this specific unit/batch
}
