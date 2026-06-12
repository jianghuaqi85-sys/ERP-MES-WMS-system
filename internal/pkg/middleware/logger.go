package middleware

import (
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// Logger returns a gin.HandlerFunc (middleware) that logs requests using uber-go/zap.
func Logger(log *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()

		fields := []zap.Field{
			zap.Int("status", status),
			zap.String("method", c.Request.Method),
			zap.String("path", path),
			zap.String("query", query),
			zap.String("ip", c.ClientIP()),
			zap.Duration("latency", latency),
			zap.String("user-agent", c.Request.UserAgent()),
		}

		// Optionally log errors attached to the gin context
		if len(c.Errors) > 0 {
			fields = append(fields, zap.String("errors", c.Errors.ByType(gin.ErrorTypePrivate).String()))
			log.Error("HTTP request error", fields...)
		} else if status >= 400 && status < 500 {
			log.Warn("HTTP request warning", fields...)
		} else if status >= 500 {
			log.Error("HTTP request failed", fields...)
		} else {
			log.Info("HTTP request", fields...)
		}
	}
}
