package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// ProductionRecord holds the schema definition for the ProductionRecord entity.
type ProductionRecord struct {
	ent.Schema
}

// Fields of the ProductionRecord.
func (ProductionRecord) Fields() []ent.Field {
	return []ent.Field{
		field.String("worker_id").NotEmpty(),
		field.Float("quantity").Default(1),
		field.String("barcode").Unique().NotEmpty(),
		field.Time("report_time").Default(time.Now),
	}
}

// Edges of the ProductionRecord.
func (ProductionRecord) Edges() []ent.Edge {
	return []ent.Edge{
		// Record belongs to a work order
		edge.From("work_order", WorkOrder.Type).
			Ref("production_records").
			Unique().
			Required(),
	}
}
