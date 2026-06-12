package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// SalesOrderItem holds the schema definition for the SalesOrderItem entity.
type SalesOrderItem struct {
	ent.Schema
}

// Fields of the SalesOrderItem.
func (SalesOrderItem) Fields() []ent.Field {
	return []ent.Field{
		field.Float("quantity").Default(1),
		field.Float("unit_price").Default(0.0),
	}
}

// Edges of the SalesOrderItem.
func (SalesOrderItem) Edges() []ent.Edge {
	return []ent.Edge{
		// Back-reference: item belongs to a SalesOrder
		edge.From("order", SalesOrder.Type).
			Ref("items").
			Unique().
			Required(),
		
		// The item sells a specific Material
		edge.To("material", Material.Type).
			Unique().
			Required(),
	}
}
