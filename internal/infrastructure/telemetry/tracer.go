package telemetry

import (
	"context"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
	"go.uber.org/fx"
	"go.uber.org/zap"
)

// ProvideTracer initializes the OpenTelemetry TracerProvider
func ProvideTracer(lc fx.Lifecycle, log *zap.Logger) (*sdktrace.TracerProvider, error) {
	// 1. Create Jaeger Exporter
	exp, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint("http://localhost:14268/api/traces")))
	if err != nil {
		return nil, err
	}

	// 2. Define the resource (service name, etc.)
	res, err := resource.Merge(
		resource.Default(),
		resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName("erp-mes-wms-go"),
			semconv.ServiceVersion("v1.0.0"),
		),
	)
	if err != nil {
		return nil, err
	}

	// 3. Create TracerProvider
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.AlwaysSample()), // In production, use probabilistic sampling
	)

	// Set as global
	otel.SetTracerProvider(tp)

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("OpenTelemetry Tracer initialized (Jaeger)")
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Shutting down TracerProvider")
			return tp.Shutdown(ctx)
		},
	})

	return tp, nil
}
