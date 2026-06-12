package middleware

import (
	"context"
	"fmt"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte("CHANGE_ME_SECRET_KEY") // Should be loaded from config

// JWTAuth middleware verifies the JWT token and extracts user info.
func JWTAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Authorization header format must be Bearer {token}"})
			return
		}

		tokenString := parts[1]
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return jwtSecret, nil
		})

		if err != nil || !token.Valid {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Invalid token claims"})
			return
		}

		// Extract user ID and role
		userID := claims["sub"]
		role := claims["role"]

		// Set in gin.Context
		c.Set("x-user-id", userID)
		c.Set("x-user-role", role)

		c.Next()
	}
}

// WrapContext bridges Gin context values to standard context
func WrapContext(c *gin.Context) context.Context {
	ctx := c.Request.Context()
	if userID, exists := c.Get("x-user-id"); exists {
		ctx = context.WithValue(ctx, "x-user-id", userID)
	}
	if role, exists := c.Get("x-user-role"); exists {
		ctx = context.WithValue(ctx, "x-user-role", role)
	}
	return ctx
}
