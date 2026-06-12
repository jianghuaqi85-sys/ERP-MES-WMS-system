package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// SalesOrder holds the schema definition for the SalesOrder entity.
type SalesOrder struct {
	ent.Schema
}

// Fields of the SalesOrder.
func (SalesOrder) Fields() []ent.Field {
	return []ent.Field{
		field.String("order_number").Unique().NotEmpty(),
		field.String("client_name").NotEmpty(),
		field.Float("total_amount").Default(0.0),
		field.String("state").Default("DRAFT"),
	}
}

// Edges of the SalesOrder.
func (SalesOrder) Edges() []ent.Edge {
	return []ent.Edge{
		// O2M: One SalesOrder has many SalesOrderItems
		edge.To("items", SalesOrderItem.Type),
	}
}
