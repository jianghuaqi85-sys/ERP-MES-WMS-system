package events

import "time"

// ProductionCompletedEvent is published when a shop-floor production report is successfully processed.
type ProductionCompletedEvent struct {
	EventID     string    `json:"event_id"`
	WorkOrderNo string    `json:"work_order_no"`
	MaterialID  int       `json:"material_id"`
	Quantity    float64   `json:"quantity"`
	Timestamp   time.Time `json:"timestamp"`
}
