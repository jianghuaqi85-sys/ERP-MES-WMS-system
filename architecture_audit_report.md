# ERP-MES-WMS Architecture Audit Report

This report documents the architectural vulnerabilities discovered during the codebase review across four dimensions: Infrastructure/Fx, Ent ORM, RESTful Handlers, and Kafka/EDA.

## R1. Infrastructure & Fx Review

**Vulnerability Discovered:** Lifecycle hook missing in Casbin Provider.
The `casbin.go` implementation did not properly register an `OnStop` lifecycle hook. This causes the underlying Ent SQLite connection to remain open when the Gin server terminates, leading to connection leaks and "database is locked" errors on restart.

**Suggested Fix Snippet:**
```go
func RegisterCasbinHook(lc fx.Lifecycle, enforcer *casbin.Enforcer, db *ent.Client) {
	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			// Initialize Casbin
			return nil
		},
		OnStop: func(ctx context.Context) error {
			// Explicitly close the Ent DB connection here
			return db.Close()
		},
	})
}
```

## R2. Application Service & Ent ORM Review

**Vulnerability Discovered 1: Missing Eager Loading (N+1 Query Issue)**
In `production_service.go`, the `WorkOrder` query now uses `Modify(...).ForUpdate()` and `WithMaterial()` to avoid nil pointer panics. In `material_service.go`, `GetBOMTree` uses eager loading with `WithChildren()`.
**Suggested Fix Snippet:**
```go
wo, err := tx.WorkOrder.Query().
	Where(workorder.ID(workOrderID)).
	WithMaterial().
	Modify(func(s *sql.Selector) { s.ForUpdate() }).
	Only(ctx)
```

**Vulnerability Discovered 2: Transaction Deadlocks and Concurrency Flaws**
In `sales_order_service.go`, a custom `defer recover()` pattern was replaced with standard `defer tx.Rollback()`. In `inventory_service.go`, pessimistic locking is performed via `Modify(...).ForUpdate()`.
**Suggested Fix Snippet (sales_order_service):**
```go
// Replace custom panic recovery with standard rollback
defer tx.Rollback()
```
**Suggested Fix Snippet (inventory_service):**
```go
inv, err := tx.Inventory.Query().
	Where(inventory.HasMaterialWith(material.ID(materialID))).
	Modify(func(s *sql.Selector) { s.ForUpdate() }).
	First(ctx)
```

## R3. RESTful Handler & DTO Review

**Vulnerability Discovered: Implicit Zero Value Overwrite & Missing Context Links**
In `inventory_dto.go`, `OrderID` was defined as `int`. If the client omits this field, Go defaults it to `0`, which the ORM interprets as an actual order ID 0. Furthermore, Handlers failed to pass down the Gin context (which contains Casbin/JWT details) to the `Application Service` layer, losing the tracing context.

**Suggested Fix Snippet (DTO):**
```go
type DeductStockReq struct {
	MaterialID int     `json:"material_id" binding:"required"`
	Quantity   float64 `json:"quantity" binding:"required,gt=0"`
	OrderID    *int    `json:"order_id,omitempty"` // Use pointer to differentiate nil vs 0
}
```

**Suggested Fix Snippet (Context):**
```go
func WrapContext(c *gin.Context) context.Context {
	ctx := c.Request.Context()
	if userID, exists := c.Get("x-user-id"); exists {
		ctx = context.WithValue(ctx, "x-user-id", userID)
	}
	return ctx
}
```

## R4. Distributed Systems & EDA Review

**Asynchronous Communication Weak Points (Kafka)**

1. **Consumer Blocking & Deserialization Panics:** 
   In `event_subscriber.go`, the Kafka consumer loops forever. If `json.Unmarshal` fails or the message processing panics, the entire consumer thread crashes and stops consuming.
   **Suggested Fix Snippet:**
   ```go
   func (s *EventSubscriber) StartListening(ctx context.Context) {
       defer func() {
           if r := recover(); r != nil {
               s.log.Error("Panic recovered in consumer", zap.Any("panic", r))
           }
       }()
       // consumer loop...
   }
   ```

2. **Message Loss Risk (Auto-Commit vs Manual Commit):**
   The consumer used `s.reader.ReadMessage(ctx)`, which automatically commits offsets *before* processing succeeds. If the DB update fails, the message is lost forever.
   **Suggested Fix Snippet:**
   ```go
   msg, err := s.reader.FetchMessage(ctx)
   // ... process message ...
   s.reader.CommitMessages(ctx, msg)
   ```

3. **Lack of Idempotency (Repeat Stock Deduction):**
   In standard Kafka setups, at-least-once delivery can cause duplicate messages. `inventory_service` did not deduplicate event IDs, which can cause stocks to be deducted multiple times for the same production run.
   **Suggested Fix Snippet:**
   ```go
   // Use SETNX in Redis for idempotency lock
   idempKey := "idemp:wms:consume:" + event.EventID
   if err := s.checker.CheckAndSet(ctx, idempKey, 24*time.Hour); err != nil {
       s.reader.CommitMessages(ctx, msg) // Already processed
       continue
   }
   ```
