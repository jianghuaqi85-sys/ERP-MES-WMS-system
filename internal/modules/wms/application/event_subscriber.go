package application

import (
	"context"
	"encoding/json"

	"github.com/segmentio/kafka-go"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/core"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/events"
	"go.uber.org/fx"
	"go.uber.org/zap"
	"time"
)

// EventSubscriber listens to domain events from Kafka and processes them in WMS
type EventSubscriber struct {
	reader     *kafka.Reader
	invService *InventoryService
	checker    *core.IdempotentChecker
	log        *zap.Logger
}

// NewEventSubscriber creates a new EventSubscriber
func NewEventSubscriber(reader *kafka.Reader, invService *InventoryService, checker *core.IdempotentChecker, log *zap.Logger) *EventSubscriber {
	return &EventSubscriber{
		reader:     reader,
		invService: invService,
		checker:    checker,
		log:        log,
	}
}

// StartListening starts the Kafka consumer loop in a background Goroutine
func (s *EventSubscriber) StartListening(ctx context.Context) {
	defer func() {
		if r := recover(); r != nil {
			s.log.Error("Panic in EventSubscriber", zap.Any("panic", r))
		}
	}()

	s.log.Info("EventSubscriber started listening to Kafka...")

	for {
		msg, err := s.reader.FetchMessage(ctx)
		if err != nil {
			if ctx.Err() != nil {
				s.log.Info("EventSubscriber shutting down gracefully")
				return
			}
			s.log.Error("Failed to fetch message from Kafka", zap.Error(err))
			continue
		}

		s.log.Info("Received Kafka message", zap.String("topic", msg.Topic), zap.String("key", string(msg.Key)))

		var event events.ProductionCompletedEvent
		if err := json.Unmarshal(msg.Value, &event); err != nil {
			s.log.Error("Failed to unmarshal event", zap.Error(err), zap.String("value", string(msg.Value)))
			s.reader.CommitMessages(ctx, msg)
			continue
		}

		idempKey := "idemp:wms:consume:" + event.EventID
		if err := s.checker.CheckAndSet(ctx, idempKey, 24*time.Hour); err != nil {
			s.reader.CommitMessages(ctx, msg)
			continue
		}

		processCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
		err = s.invService.DeductStock(processCtx, event.MaterialID, event.Quantity, 0)
		cancel()

		if err != nil {
			s.log.Error("Failed to deduct stock", zap.Error(err), zap.String("event_id", event.EventID))
			s.checker.Clear(ctx, idempKey)
		} else {
			s.reader.CommitMessages(ctx, msg)
			s.log.Info("Successfully processed ProductionCompletedEvent", zap.String("event_id", event.EventID))
		}
	}
}

// RegisterSubscriberHook registers the consumer loop with Fx
func RegisterSubscriberHook(lc fx.Lifecycle, sub *EventSubscriber) {
	var cancel context.CancelFunc

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			// We create a detached context for the infinite loop so it survives OnStart
			var loopCtx context.Context
			loopCtx, cancel = context.WithCancel(context.Background())
			
			go sub.StartListening(loopCtx)
			return nil
		},
		OnStop: func(ctx context.Context) error {
			if cancel != nil {
				cancel()
			}
			return nil
		},
	})
}
