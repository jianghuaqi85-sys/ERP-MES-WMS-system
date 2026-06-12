package casbin

import (
	"context"
	"fmt"

	"github.com/casbin/casbin/v2"
	entadapter "github.com/casbin/ent-adapter"
	"github.com/yourorg/erp-mes-wms-go/ent"
	"go.uber.org/fx"
	"go.uber.org/zap"
)

// ProvideEnforcer initializes the Casbin Enforcer using the Ent adapter.
func ProvideEnforcer(lc fx.Lifecycle, client *ent.Client, log *zap.Logger) (*casbin.Enforcer, error) {
	// Initialize the ent adapter using the existing ent.Client's driver
	// (casbin/ent-adapter/v2 works well with existing ent connections or DSN)
	// For simplicity in this Fx setup, we instruct the adapter to use the same SQLite DSN
	// In production, we can pass the existing sql.DB to the adapter
	
	dsn := "file:erp.db?cache=shared&mode=rwc&_pragma=foreign_keys(1)"
	adapter, err := entadapter.NewAdapter("sqlite3", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to create casbin ent adapter: %w", err)
	}

	enforcer, err := casbin.NewEnforcer("configs/rbac_model.conf", adapter)
	if err != nil {
		return nil, fmt.Errorf("failed to create casbin enforcer: %w", err)
	}

	// Load policies from DB
	err = enforcer.LoadPolicy()
	if err != nil {
		return nil, fmt.Errorf("failed to load casbin policies: %w", err)
	}

	// Enable auto-save so changes in memory are persisted to the database
	enforcer.EnableAutoSave(true)

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("Casbin Enforcer started")
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Closing Casbin Enforcer resources")
			return nil
		},
	})

	log.Info("Casbin Enforcer initialized successfully with Ent adapter")

	return enforcer, nil
}
