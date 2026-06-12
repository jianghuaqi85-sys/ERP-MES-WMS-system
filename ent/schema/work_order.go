package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// WorkOrder holds the schema definition for the WorkOrder entity.
type WorkOrder struct {
	ent.Schema
}

// Fields of the WorkOrder.
func (WorkOrder) Fields() []ent.Field {
	return []ent.Field{
		field.String("order_no").Unique().NotEmpty(),
		field.Float("plan_qty").Default(1),
		field.Float("produced_qty").Default(0),
		field.String("status").Default("PENDING"), // PENDING, IN_PROGRESS, COMPLETED
	}
}

// Edges of the WorkOrder.
func (WorkOrder) Edges() []ent.Edge {
	return []ent.Edge{
		// What material is being produced
		edge.To("material", Material.Type).
			Unique().
			Required(),
		
		// One work order has many production records
		edge.To("production_records", ProductionRecord.Type),
	}
}
