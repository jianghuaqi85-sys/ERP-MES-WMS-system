package application

import (
	"context"
	"errors"
	"fmt"
	"github.com/redis/go-redis/v9"
	"github.com/yourorg/erp-mes-wms-go/ent"
	"github.com/yourorg/erp-mes-wms-go/ent/inventory"
	"github.com/yourorg/erp-mes-wms-go/ent/material"
	"go.uber.org/zap"
	"entgo.io/ent/dialect/sql"
)

var (
	ErrInsufficientStock = errors.New("insufficient stock")
	ErrConcurrentUpdate  = errors.New("concurrent update conflict, please retry")
	ErrInventoryNotFound = errors.New("inventory not found")
)

// InventoryService handles WMS inventory operations
type InventoryService struct {
	db  *ent.Client
	rdb *redis.Client
	log *zap.Logger
}

// NewInventoryService creates a new InventoryService
func NewInventoryService(db *ent.Client, rdb *redis.Client, log *zap.Logger) *InventoryService {
	return &InventoryService{db: db, rdb: rdb, log: log}
}

// Lua script for atomic stock deduction in Redis.
// KEYS[1] = inventory key (e.g. "stock:material:{id}")
// ARGV[1] = deduct quantity
// Returns: 1 if success, 0 if insufficient stock, -1 if key does not exist.
const deductStockScript = `
local stock = redis.call("GET", KEYS[1])
if stock == false then
	return -1
end
local qty = tonumber(stock)
local deduct = tonumber(ARGV[1])
if qty >= deduct then
	redis.call("DECRBY", KEYS[1], deduct)
	return 1
else
	return 0
end
`

// DeductStock performs atomic deduction via Redis and optimistic locking via DB
func (s *InventoryService) DeductStock(ctx context.Context, materialID int, qty float64, orderID int) error {
	// 1. 【Redis 预扣减】
	// In a real system, you'd cache the stock into Redis beforehand. 
	// For this exercise, assume the key exists if the cache is hot.
	cacheKey := fmt.Sprintf("stock:material:%d", materialID)
	
	// We'll execute the script
	result, err := s.rdb.Eval(ctx, deductStockScript, []string{cacheKey}, int64(qty)).Result()
	if err == nil {
		resInt := result.(int64)
		if resInt == 0 {
			return ErrInsufficientStock
		}
		// If resInt == -1, cache miss. We should ideally load it from DB, lock it, and put it in Redis.
		// For simplicity, if cache miss, we just fallback to DB directly below.
	} else {
		// Log redis error but fallback to DB to avoid full outage
		s.log.Warn("Redis eval failed, falling back to DB", zap.Error(err))
	}

	// 2. 【DB 最终落地 & 并发锁 & 记录流水】
	err = s.deductDB(ctx, materialID, qty, orderID)
	if err != nil {
		// Compensate Redis on DB failure
		if result != nil && result.(int64) == 1 {
			s.rdb.IncrBy(ctx, cacheKey, int64(qty))
			s.log.Warn("DB deduction failed, compensated Redis cache", zap.Int("material_id", materialID), zap.Error(err))
		}
		return err
	}

	return nil
}

func (s *InventoryService) deductDB(ctx context.Context, materialID int, qty float64, orderID int) error {
	tx, err := s.db.Tx(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Find the inventory record (we assume there's one primary location for simplicity)
	inv, err := tx.Inventory.Query().
		Where(inventory.HasMaterialWith(material.ID(materialID))).
		Modify(func(s *sql.Selector) { s.ForUpdate() }).
		First(ctx)

	if err != nil {
		if ent.IsNotFound(err) {
			return ErrInventoryNotFound
		}
		return err
	}

	if inv.Quantity < qty {
		return ErrInsufficientStock
	}

	// 3. 【DB 最终更新】
	currentVersion := inv.Version
	
	_, err = tx.Inventory.Update().
		Where(inventory.ID(inv.ID)).
		AddQuantity(-qty).
		SetVersion(currentVersion + 1). // Increment version
		Save(ctx)

	if err != nil {
		return fmt.Errorf("failed to update inventory: %w", err)
	}

	// 4. 【记录流水】 - StockRecord
	err = tx.StockRecord.Create().
		SetInventory(inv).
		SetChangeQty(-qty).
		SetRecordType("OUTBOUND").
		SetReferenceOrderID(orderID).
		Exec(ctx)

	if err != nil {
		return fmt.Errorf("failed to create stock record: %w", err)
	}

	return tx.Commit()
}
