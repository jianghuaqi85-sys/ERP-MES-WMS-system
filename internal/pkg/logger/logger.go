package logger

import (
	"github.com/yourorg/erp-mes-wms-go/internal/config"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// ProvideLogger creates and returns a zap.Logger instance based on the configuration.
// It is designed to be used as a provider in fx.
func ProvideLogger(cfg *config.Config) (*zap.Logger, error) {
	var zapConfig zap.Config

	if cfg.Server.Mode == "production" {
		zapConfig = zap.NewProductionConfig()
	} else {
		zapConfig = zap.NewDevelopmentConfig()
	}

	// Override logging level based on config
	level, err := zapcore.ParseLevel(cfg.Logger.Level)
	if err == nil {
		zapConfig.Level = zap.NewAtomicLevelAt(level)
	}

	// Override encoding
	if cfg.Logger.Encoding != "" {
		zapConfig.Encoding = cfg.Logger.Encoding
	}

	// Provide both console and file outputs (for demonstration, output to stdout)
	// In a real scenario, you'd configure OutputPaths to include a file path like "logs/app.log"
	zapConfig.OutputPaths = []string{"stdout"}
	zapConfig.ErrorOutputPaths = []string{"stderr"}

	logger, err := zapConfig.Build()
	if err != nil {
		return nil, err
	}

	return logger, nil
}
