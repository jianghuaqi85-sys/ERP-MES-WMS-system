package application

import (
	"fmt"

	"github.com/casbin/casbin/v2"
	"go.uber.org/zap"
)

// RoleService handles RBAC role assignments and policy management.
type RoleService struct {
	enforcer *casbin.Enforcer
	log      *zap.Logger
}

// NewRoleService creates a new RoleService.
func NewRoleService(enforcer *casbin.Enforcer, log *zap.Logger) *RoleService {
	return &RoleService{
		enforcer: enforcer,
		log:      log,
	}
}

// AddPolicyToRole adds a new permission policy to a specific role in a domain.
func (s *RoleService) AddPolicyToRole(role, domain, path, method string) (bool, error) {
	s.log.Info("Adding policy to role", zap.String("role", role), zap.String("path", path), zap.String("method", method))
	
	// Because AutoSave is true, this will write to the database
	added, err := s.enforcer.AddPolicy(role, domain, path, method)
	if err != nil {
		return false, fmt.Errorf("failed to add policy: %w", err)
	}

	return added, nil
}
