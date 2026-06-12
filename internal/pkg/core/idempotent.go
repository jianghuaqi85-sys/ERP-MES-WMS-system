package core

import (
	"context"
	"errors"
	"time"

	"github.com/redis/go-redis/v9"
)

var ErrIdempotentConflict = errors.New("request is already being processed or has been completed")

// IdempotentChecker provides methods to ensure idempotency of operations using Redis
type IdempotentChecker struct {
	rdb *redis.Client
}

// NewIdempotentChecker creates a new checker
func NewIdempotentChecker(rdb *redis.Client) *IdempotentChecker {
	return &IdempotentChecker{rdb: rdb}
}

// CheckAndSet tries to set a key in Redis. If the key already exists, it returns ErrIdempotentConflict.
// It uses SETNX internally.
func (c *IdempotentChecker) CheckAndSet(ctx context.Context, uniqueKey string, ttl time.Duration) error {
	success, err := c.rdb.SetNX(ctx, uniqueKey, "1", ttl).Result()
	if err != nil {
		return err
	}
	if !success {
		return ErrIdempotentConflict
	}
	return nil
}

// Clear allows manually removing the idempotency key, e.g. in case of a business error where a retry is desired.
func (c *IdempotentChecker) Clear(ctx context.Context, uniqueKey string) error {
	return c.rdb.Del(ctx, uniqueKey).Err()
}
