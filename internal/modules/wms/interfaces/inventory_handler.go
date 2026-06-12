package interfaces

import (
	"net/http"

	"github.com/casbin/casbin/v2"
	"github.com/gin-gonic/gin"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/wms/application"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/wms/domain/dto"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/middleware"
	"go.uber.org/zap"
)

// InventoryHandler exposes inventory endpoints
type InventoryHandler struct {
	service *application.InventoryService
	log     *zap.Logger
}

// NewInventoryHandler creates the handler
func NewInventoryHandler(service *application.InventoryService, log *zap.Logger) *InventoryHandler {
	return &InventoryHandler{service: service, log: log}
}

// RegisterWMSRoutes registers the WMS routes on the given gin.Engine
func RegisterWMSRoutes(r *gin.Engine, handler *InventoryHandler, enforcer *casbin.Enforcer, log *zap.Logger) {
	api := r.Group("/api/v1")
	
	wmsGroup := api.Group("/wms")
	// Apply JWT and Casbin Authz middlewares to all WMS routes
	wmsGroup.Use(middleware.JWTAuth(), middleware.Authz(enforcer, log))
	{
		wmsGroup.POST("/inventory/deduct", handler.DeductStock)
	}
}

func (h *InventoryHandler) DeductStock(c *gin.Context) {
	var req dto.DeductStockReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	orderID := 0
	if req.OrderID != nil {
		orderID = *req.OrderID
	}

	err := h.service.DeductStock(middleware.WrapContext(c), req.MaterialID, req.Quantity, orderID)
	if err != nil {
		if err == application.ErrInsufficientStock {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		if err == application.ErrConcurrentUpdate {
			c.JSON(http.StatusConflict, gin.H{"error": "System is busy, please try again later"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Stock deducted successfully"})
}
