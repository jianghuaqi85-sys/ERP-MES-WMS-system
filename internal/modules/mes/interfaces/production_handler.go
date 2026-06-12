package interfaces

import (
	"net/http"
	"strconv"

	"github.com/casbin/casbin/v2"
	"github.com/gin-gonic/gin"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/mes/application"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/mes/domain/dto"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/middleware"
	"go.uber.org/zap"
)

// ProductionHandler exposes MES endpoints
type ProductionHandler struct {
	service *application.ProductionService
	log     *zap.Logger
}

// NewProductionHandler creates the handler
func NewProductionHandler(service *application.ProductionService, log *zap.Logger) *ProductionHandler {
	return &ProductionHandler{service: service, log: log}
}

// RegisterMESRoutes registers the MES routes on the given gin.Engine
func RegisterMESRoutes(r *gin.Engine, handler *ProductionHandler, enforcer *casbin.Enforcer, log *zap.Logger) {
	api := r.Group("/api/v1")
	
	mesGroup := api.Group("/mes")
	// Apply JWT and Casbin Authz middlewares to all MES routes
	mesGroup.Use(middleware.JWTAuth(), middleware.Authz(enforcer, log))
	{
		mesGroup.POST("/work-orders/:id/report", handler.ReportProduction)
	}
}

func (h *ProductionHandler) ReportProduction(c *gin.Context) {
	idStr := c.Param("id")
	woID, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid work order ID"})
		return
	}

	var req dto.ReportProductionReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err = h.service.ReportProduction(middleware.WrapContext(c), woID, &req)
	if err != nil {
		c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Production reported successfully"})
}
