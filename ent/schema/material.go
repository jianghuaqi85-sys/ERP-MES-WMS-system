package schema

import (
	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// Material holds the schema definition for the Material entity.
type Material struct {
	ent.Schema
}

// Fields of the Material.
func (Material) Fields() []ent.Field {
	return []ent.Field{
		field.String("material_code").Unique().NotEmpty(),
		field.String("name").NotEmpty(),
		field.Enum("type").Values("raw", "semi", "finished").Default("raw"),
		field.String("specifications").Optional(),
	}
}

// Edges of the Material.
func (Material) Edges() []ent.Edge {
	return []ent.Edge{
		// BOM Tree: self-referencing edge
		// A material can have many children (components)
		edge.To("children", Material.Type).
			From("parent").
			Unique(),
		// Back-reference: A material belongs to many inventories
		edge.From("inventories", Inventory.Type).
			Ref("material"),
	}
}
