package middleware

import (
	"net/http"

	"github.com/casbin/casbin/v2"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// Authz creates a Casbin authorization middleware
func Authz(enforcer *casbin.Enforcer, log *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// x-user-role is set by the JWT middleware
		roleVal, exists := c.Get("x-user-role")
		if !exists {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized: role not found in context"})
			return
		}

		role := roleVal.(string)
		
		// In a real multi-tenant system, this would be extracted from the user info or request header
		// For now, we assume a default domain "tenant1"
		domain := "tenant1" 
		
		obj := c.Request.URL.Path
		act := c.Request.Method

		// Ask Casbin
		allowed, err := enforcer.Enforce(role, domain, obj, act)
		if err != nil {
			log.Error("Casbin enforcement error", zap.Error(err))
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "Internal server error during authorization"})
			return
		}

		if !allowed {
			log.Warn("Access denied by Casbin", zap.String("role", role), zap.String("domain", domain), zap.String("obj", obj), zap.String("act", act))
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "Forbidden: you do not have permission to access this resource"})
			return
		}

		c.Next()
	}
}
