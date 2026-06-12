package interfaces

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/yourorg/erp-mes-wms-go/ent"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/middleware"
)

var jwtSecret = []byte("CHANGE_ME_SECRET_KEY")

// RegisterAuthRoutes mounts the auth endpoints onto the given router group.
// It acts as an Fx invoke function.
func RegisterAuthRoutes(r *gin.Engine, dbClient *ent.Client) {
	api := r.Group("/api/v1")
	
	authGroup := api.Group("/auth")
	{
		authGroup.POST("/login", loginHandler)
		authGroup.GET("/me", middleware.JWTAuth(), meHandler)
	}
}

type loginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

func loginHandler(c *gin.Context) {
	var req loginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Mock authentication
	if req.Username != "admin" || req.Password != "123456" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// Generate JWT
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"sub":  "1",       // UserID
		"role": "ADMIN",   // Role
		"exp":  time.Now().Add(time.Hour * 24).Unix(),
	})

	tokenString, err := token.SignedString(jwtSecret)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"access_token": tokenString,
		"token_type":   "Bearer",
	})
}

func meHandler(c *gin.Context) {
	// Retrieve info injected by the JWT middleware
	userID, _ := c.Get("x-user-id")
	role, _ := c.Get("x-user-role")

	c.JSON(http.StatusOK, gin.H{
		"user_id": userID,
		"role":    role,
	})
}
