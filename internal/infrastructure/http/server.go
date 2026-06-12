package http

import (
	"context"
	"errors"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/yourorg/erp-mes-wms-go/internal/config"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/middleware"
	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.uber.org/fx"
	"go.uber.org/zap"
    "github.com/yourorg/erp-mes-wms-go/internal/infrastructure/telemetry"
)

// ProvideHTTPServer initializes the Gin engine and registers it with the Fx lifecycle.
func ProvideHTTPServer(lc fx.Lifecycle, cfg *config.Config, log *zap.Logger) *gin.Engine {
	if cfg.Server.Mode == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()

	// Mount global middlewares
	r.Use(otelgin.Middleware("erp-mes-wms-go"), middleware.Logger(log), middleware.CORS(), gin.Recovery())
	r.Use(middleware.Logger(log))
	r.Use(middleware.CORS())
	telemetry.RegisterMetrics(r)

	// Set up the HTTP server
	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", cfg.Server.Port),
		Handler: r,
	}

	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info("Starting HTTP server", zap.Int("port", cfg.Server.Port))
			go func() {
				if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
					log.Fatal("HTTP server failed", zap.Error(err))
				}
			}()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info("Stopping HTTP server gracefully")
			return srv.Shutdown(ctx)
		},
	})

	return r
}
