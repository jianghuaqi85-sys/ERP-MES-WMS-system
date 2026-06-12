package db

import (
	"context"
	"fmt"

	"github.com/yourorg/erp-mes-wms-go/ent"
	"github.com/yourorg/erp-mes-wms-go/internal/config"
	"go.uber.org/fx"
	"go.uber.org/zap"

	_ "modernc.org/sqlite" // Pure Go SQLite driver
)

// ProvideDB initializes and returns the Ent ORM client.
// It also registers lifecycle hooks to open the connection and run migrations on start, and close on stop.
func ProvideDB(lc fx.Lifecycle, cfg *config.Config, log *zap.Logger) (*ent.Client, error) {
	// For demonstration, using an in-memory SQLite database or a local file based on config.
	// In a real app, DSN would be read from cfg.Database.DSN
	dsn := "file:erp.db?cache=shared&mode=rwc&_pragma=foreign_keys(1)"

	client, err := ent.Open("sqlite", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed opening connection to sqlite: %w", err)
	}

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("Connecting to database and running migrations...")
			// Run schema migration
			if err := client.Schema.Create(ctx); err != nil {
				return fmt.Errorf("failed creating schema resources: %w", err)
			}
			log.Info("Database migrations completed successfully")
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Closing database connection")
			return client.Close()
		},
	})

	return client, nil
}
