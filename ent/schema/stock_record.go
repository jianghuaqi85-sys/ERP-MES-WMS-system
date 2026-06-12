package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// StockRecord holds the schema definition for the StockRecord entity.
type StockRecord struct {
	ent.Schema
}

// Fields of the StockRecord.
func (StockRecord) Fields() []ent.Field {
	return []ent.Field{
		field.Float("change_qty"), // positive for inbound, negative for outbound
		field.String("record_type").Default("OUTBOUND"), // INBOUND, OUTBOUND, STOCKTAKE
		field.Int("reference_order_id").Optional(), // Associated order (SalesOrder or WorkOrder)
	}
}

// Edges of the StockRecord.
func (StockRecord) Edges() []ent.Edge {
	return []ent.Edge{
		// The inventory record this stock history belongs to
		edge.From("inventory", Inventory.Type).
			Ref("stock_records").
			Unique().
			Required(),
	}
}
