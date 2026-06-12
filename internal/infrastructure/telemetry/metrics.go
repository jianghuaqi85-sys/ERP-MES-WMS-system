package telemetry

import (
	"context"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/sdk/metric"
	"go.uber.org/fx"
	"go.uber.org/zap"
)

var exporter *prometheus.Exporter



// ProvideMetrics initializes the OpenTelemetry MeterProvider for Prometheus
func ProvideMetrics(lc fx.Lifecycle, log *zap.Logger) (*metric.MeterProvider, error) {
	// Create Prometheus exporter (global variable)
	var err error
	exporter, err = prometheus.New()
	if err != nil {
		return nil, err
	}
	provider := metric.NewMeterProvider(metric.WithReader(exporter))
	otel.SetMeterProvider(provider)

	lc.Append(fx.Hook{ // Register lifecycle hooks
		OnStart: func(ctx context.Context) error {
			log.Info("OpenTelemetry Metrics initialized (Prometheus)")
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Shutting down MeterProvider")
			return provider.Shutdown(ctx)
		},
	})

	return provider, nil
}

func RegisterMetrics(r *gin.Engine) {
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))
}
