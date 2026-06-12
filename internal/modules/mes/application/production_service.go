package application

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/yourorg/erp-mes-wms-go/ent"
	"github.com/yourorg/erp-mes-wms-go/ent/workorder"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/mes/domain/dto"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/core"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/events"
	"go.uber.org/zap"
	"entgo.io/ent/dialect/sql"
)

// ProductionService handles MES production and reporting logic
type ProductionService struct {
	db          *ent.Client
	checker     *core.IdempotentChecker
	kafkaWriter *kafka.Writer
	log         *zap.Logger
}

// NewProductionService creates a new ProductionService
func NewProductionService(db *ent.Client, checker *core.IdempotentChecker, kafkaWriter *kafka.Writer, log *zap.Logger) *ProductionService {
	return &ProductionService{
		db:          db,
		checker:     checker,
		kafkaWriter: kafkaWriter,
		log:         log,
	}
}

// ReportProduction handles high-frequency production reporting from shop floor
func (s *ProductionService) ReportProduction(ctx context.Context, workOrderID int, req *dto.ReportProductionReq) error {
	// 1. 【幂等拦截】 (Idempotency Check)
	// Key is based on the unique barcode scanned
	idempKey := fmt.Sprintf("idemp:mes:report:%s", req.Barcode)
	
	// Try to acquire the lock/flag for 24 hours (prevents double scanning of the same barcode)
	err := s.checker.CheckAndSet(ctx, idempKey, 24*time.Hour)
	if err != nil {
		if err == core.ErrIdempotentConflict {
			s.log.Warn("Idempotent check failed: duplicate report detected", zap.String("barcode", req.Barcode))
			return fmt.Errorf("duplicate production report for barcode: %s", req.Barcode)
		}
		return fmt.Errorf("idempotency check failed: %w", err)
	}

	// 2. 【聚合流转】开启 Ent 事务
	tx, err := s.db.Tx(ctx)
	if err != nil {
		s.checker.Clear(ctx, idempKey) // Release if we fail early
		return fmt.Errorf("failed to start tx: %w", err)
	}
	defer func() {
		if v := recover(); v != nil {
			tx.Rollback()
			panic(v)
		}
	}()

	// Query WorkOrder for update
	wo, err := tx.WorkOrder.Query().
		Where(workorder.ID(workOrderID)).
		WithMaterial().
		Modify(func(s *sql.Selector) {
			s.ForUpdate()
		}).
		Only(ctx)

	if err != nil {
		tx.Rollback()
		s.checker.Clear(ctx, idempKey)
		return fmt.Errorf("failed to query work order: %w", err)
	}

	if wo.Status == "COMPLETED" {
		tx.Rollback()
		s.checker.Clear(ctx, idempKey)
		return fmt.Errorf("work order %s is already completed", wo.OrderNo)
	}

	// 3. 写入 ProductionRecord
	_, err = tx.ProductionRecord.Create().
		SetWorkOrder(wo).
		SetWorkerID(req.WorkerID).
		SetQuantity(req.Quantity).
		SetBarcode(req.Barcode).
		Save(ctx)

	if err != nil {
		tx.Rollback()
		s.checker.Clear(ctx, idempKey)
		return fmt.Errorf("failed to save production record: %w", err)
	}

	// 4. 更新 WorkOrder 的 ProducedQty 和 Status
	newProducedQty := wo.ProducedQty + req.Quantity
	newStatus := "IN_PROGRESS"
	if newProducedQty >= wo.PlanQty {
		newStatus = "COMPLETED"
	} else if wo.Status == "PENDING" {
		newStatus = "IN_PROGRESS"
	}

	_, err = tx.WorkOrder.UpdateOne(wo).
		SetProducedQty(newProducedQty).
		SetStatus(newStatus).
		Save(ctx)

	if err != nil {
		tx.Rollback()
		s.checker.Clear(ctx, idempKey)
		return fmt.Errorf("failed to update work order: %w", err)
	}

	// 5. 【跨模块协作】: 发布领域事件 (Publish Domain Event)
	event := events.ProductionCompletedEvent{
		EventID:     req.Barcode, // Using barcode as a simple event ID for traceability
		WorkOrderNo: wo.OrderNo,
		MaterialID:  wo.Edges.Material.ID, // Assuming eagerly loaded or we can just fetch it. Wait, Material might not be preloaded.
		Quantity:    req.Quantity,
		Timestamp:   time.Now(),
	}

	eventBytes, err := json.Marshal(event)
	if err != nil {
		tx.Rollback()
		s.checker.Clear(ctx, idempKey)
		return fmt.Errorf("failed to serialize event: %w", err)
	}

	// 6. 提交事务
	if err := tx.Commit(); err != nil {
		s.checker.Clear(ctx, idempKey)
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	// Emit event after successful commit to avoid ghost events
	err = s.kafkaWriter.WriteMessages(context.Background(), kafka.Message{
		Key:   []byte(wo.OrderNo),
		Value: eventBytes,
	})
	if err != nil {
		s.log.Error("Failed to publish ProductionCompletedEvent immediately, scheduling background retry", zap.Error(err), zap.String("barcode", req.Barcode))
		go func(key []byte, val []byte, barcode string) {
			for i := 1; i <= 5; i++ {
				time.Sleep(time.Duration(i) * time.Second) // exponential-like backoff
				err := s.kafkaWriter.WriteMessages(context.Background(), kafka.Message{Key: key, Value: val})
				if err == nil {
					s.log.Info("Published ProductionCompletedEvent after retry", zap.String("barcode", barcode))
					return
				}
			}
			s.log.Error("CRITICAL: Message permanently lost after retries", zap.String("barcode", barcode))
		}([]byte(wo.OrderNo), eventBytes, req.Barcode)
	} else {
		s.log.Info("Published ProductionCompletedEvent", zap.String("barcode", req.Barcode))
	}

	s.log.Info("Production reported successfully", zap.String("barcode", req.Barcode), zap.Float64("qty", req.Quantity))
	return nil
}
