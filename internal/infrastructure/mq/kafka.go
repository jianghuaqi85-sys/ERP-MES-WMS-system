package mq

import (
	"context"

	"github.com/segmentio/kafka-go"
	"go.uber.org/fx"
	"go.uber.org/zap"
)

// ProvideKafkaWriter creates a Kafka producer
func ProvideKafkaWriter(lc fx.Lifecycle, log *zap.Logger) *kafka.Writer {
	// In production, broker config should come from config file
	w := &kafka.Writer{
		Addr:                   kafka.TCP("localhost:9092"),
		Topic:                  "mes.production.completed",
		AllowAutoTopicCreation: true,
	}

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("Kafka Writer initialized")
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Closing Kafka Writer")
			return w.Close()
		},
	})

	return w
}

// ProvideKafkaReader creates a Kafka consumer
func ProvideKafkaReader(lc fx.Lifecycle, log *zap.Logger) *kafka.Reader {
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers: []string{"localhost:9092"},
		GroupID: "wms-inventory-group",
		Topic:   "mes.production.completed",
	})

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("Kafka Reader initialized")
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Closing Kafka Reader")
			return r.Close()
		},
	})

	return r
}
