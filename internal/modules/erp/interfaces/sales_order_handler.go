package interfaces

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/application"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/domain/dto"
	"github.com/yourorg/erp-mes-wms-go/internal/modules/erp/domain/valobj"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/middleware"
	"go.uber.org/zap"
)

// SalesOrderHandler exposes sales order endpoints
type SalesOrderHandler struct {
	service *application.SalesOrderService
	log     *zap.Logger
}

// NewSalesOrderHandler creates the handler
func NewSalesOrderHandler(service *application.SalesOrderService, log *zap.Logger) *SalesOrderHandler {
	return &SalesOrderHandler{service: service, log: log}
}

func (h *SalesOrderHandler) CreateOrder(c *gin.Context) {
	var req dto.CreateSalesOrderReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	order, err := h.service.CreateOrder(middleware.WrapContext(c), &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"data": order})
}

func (h *SalesOrderHandler) ApproveOrder(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid order ID"})
		return
	}

	err = h.service.ApproveOrder(middleware.WrapContext(c), id)
	if err != nil {
		if err == valobj.ErrInvalidStateTransition {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Order approved successfully"})
}

func (h *SalesOrderHandler) GetOrder(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid order ID"})
		return
	}

	order, err := h.service.GetOrder(middleware.WrapContext(c), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": order})
}
