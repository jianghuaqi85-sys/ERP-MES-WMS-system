package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// Inventory holds the schema definition for the Inventory entity.
type Inventory struct {
	ent.Schema
}

// Fields of the Inventory.
func (Inventory) Fields() []ent.Field {
	return []ent.Field{
		field.Float("quantity").Default(0),
		field.String("warehouse").Default("MAIN"),
		field.String("location_code").NotEmpty(),
		field.String("batch_number").Optional(),
		// Optimistic locking version
		field.Int64("version").Default(0),
	}
}

// Edges of the Inventory.
func (Inventory) Edges() []ent.Edge {
	return []ent.Edge{
		// An inventory record belongs to one material
		edge.To("material", Material.Type).
			Unique().
			Required(),
		
		// One inventory can have many stock records (history)
		edge.To("stock_records", StockRecord.Type),
	}
}
