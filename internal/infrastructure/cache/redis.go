package cache

import (
	"context"

	"github.com/redis/go-redis/v9"
	"go.uber.org/fx"
	"go.uber.org/zap"
)

// ProvideRedis initializes a Redis client and registers it with Fx lifecycle.
func ProvideRedis(lc fx.Lifecycle, log *zap.Logger) (*redis.Client, error) {
	// In production, read from config. For now, use default localhost:6379
	rdb := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "", // no password set
		DB:       0,  // use default DB
	})

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("Connecting to Redis...")
			// Test connection
			if err := rdb.Ping(ctx).Err(); err != nil {
				log.Warn("Failed to connect to Redis. Pre-deduction might fail if redis is offline", zap.Error(err))
				// We don't return error here to allow the app to start even if redis is down (in dev mode)
				// In production, we'd probably want to return err to prevent startup if cache is strictly required
			} else {
				log.Info("Redis connected successfully")
			}
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Closing Redis connection")
			return rdb.Close()
		},
	})

	return rdb, nil
}
