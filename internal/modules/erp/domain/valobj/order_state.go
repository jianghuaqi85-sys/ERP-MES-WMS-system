package valobj

import "errors"

// OrderState represents the state of a sales order.
type OrderState string

const (
	StateDraft           OrderState = "DRAFT"
	StatePendingApproval OrderState = "PENDING_APPROVAL"
	StateApproved        OrderState = "APPROVED"
	StateCompleted       OrderState = "COMPLETED"
	StateCancelled       OrderState = "CANCELLED"
)

var ErrInvalidStateTransition = errors.New("invalid order state transition")

// CanTransition checks if the transition from a current state to a target state is valid.
func CanTransition(from, to OrderState) bool {
	switch from {
	case StateDraft:
		// Draft can only be submitted for approval or cancelled
		return to == StatePendingApproval || to == StateCancelled
	case StatePendingApproval:
		// Pending can be approved, rejected (back to draft), or cancelled
		return to == StateApproved || to == StateDraft || to == StateCancelled
	case StateApproved:
		// Approved can go to completed
		return to == StateCompleted
	case StateCompleted:
		// Terminal state
		return false
	case StateCancelled:
		// Terminal state
		return false
	default:
		return false
	}
}
