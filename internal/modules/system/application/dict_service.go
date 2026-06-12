package application

import (
	"context"
)

// DictService provides basic data dictionary capabilities.
type DictService struct {
}

func NewDictService() *DictService {
	return &DictService{}
}

// GetDictItems simulates fetching dictionary items (e.g., material types, statuses).
func (s *DictService) GetDictItems(ctx context.Context, dictCode string) []string {
	// Simulated dictionary
	switch dictCode {
	case "material_type":
		return []string{"raw", "semi", "finished"}
	case "work_order_status":
		return []string{"PLANNED", "IN_PROGRESS", "COMPLETED", "CLOSED"}
	default:
		return nil
	}
}
