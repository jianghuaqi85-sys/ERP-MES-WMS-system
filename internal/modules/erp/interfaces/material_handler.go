package interfaces

import (
	"net/http"
	"strconv"

	"github.com/casbin/casbin/v2"
	"github.com/gin-gonic/gin"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/application"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/domain/dto"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/middleware"
	"go.uber.org/zap"
)

// MaterialHandler exposes material-related endpoints
type MaterialHandler struct {
	service *application.MaterialService
	log     *zap.Logger
}

// NewMaterialHandler creates the handler
func NewMaterialHandler(service *application.MaterialService, log *zap.Logger) *MaterialHandler {
	return &MaterialHandler{service: service, log: log}
}

// RegisterERPRoutes registers the ERP routes on the given gin.Engine
func RegisterERPRoutes(r *gin.Engine, handler *MaterialHandler, orderHandler *SalesOrderHandler, enforcer *casbin.Enforcer, log *zap.Logger) {
	api := r.Group("/api/v1")
	
	erpGroup := api.Group("/erp")
	// Apply JWT and Casbin Authz middlewares to all ERP routes
	erpGroup.Use(middleware.JWTAuth(), middleware.Authz(enforcer, log))
	{
		erpGroup.POST("/materials", handler.CreateMaterial)
		erpGroup.POST("/materials/:id/bom", handler.AddBOM)
		erpGroup.GET("/materials/:id/bom", handler.GetBOM)

		erpGroup.POST("/sales-orders", orderHandler.CreateOrder)
		erpGroup.POST("/sales-orders/:id/approve", orderHandler.ApproveOrder)
		erpGroup.GET("/sales-orders/:id", orderHandler.GetOrder)
	}
}

func (h *MaterialHandler) CreateMaterial(c *gin.Context) {
	var req dto.CreateMaterialReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	mat, err := h.service.CreateMaterial(middleware.WrapContext(c), &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"data": mat})
}

func (h *MaterialHandler) AddBOM(c *gin.Context) {
	parentIDStr := c.Param("id")
	parentID, err := strconv.Atoi(parentIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid parent ID"})
		return
	}

	var req dto.AddBOMReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err = h.service.AddBOMComponent(middleware.WrapContext(c), parentID, req.ChildID, req.Quantity)
	if err != nil {
		if err == dto.ErrBOMCycleDetected {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "BOM component added successfully"})
}

func (h *MaterialHandler) GetBOM(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid material ID"})
		return
	}

	tree, err := h.service.GetBOMTree(middleware.WrapContext(c), id)
	if err != nil {
		if err == dto.ErrMaterialNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": tree})
}
