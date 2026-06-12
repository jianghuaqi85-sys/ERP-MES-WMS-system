package main

import (
	"github.com/yourorg/erp-mes-wms-go/internal/config"
	"github.com/yourorg/erp-mes-wms-go/internal/infrastructure/cache"
	"github.com/yourorg/erp-mes-wms-go/internal/infrastructure/casbin"
	"github.com/yourorg/erp-mes-wms-go/internal/infrastructure/db"
	"github.com/yourorg/erp-mes-wms-go/internal/infrastructure/http"
	"github.com/yourorg/erp-mes-wms-go/internal/infrastructure/mq"
	"github.com/yourorg/erp-mes-wms-go/internal/infrastructure/telemetry"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/core"
	erpApp "github.com/yourorg/erp-mes-wms-go/internal/modules/erp/application"
	erpIntf "github.com/yourorg/erp-mes-wms-go/internal/modules/erp/interfaces"
	mesApp "github.com/yourorg/erp-mes-wms-go/internal/modules/mes/application"
	mesIntf "github.com/yourorg/erp-mes-wms-go/internal/modules/mes/interfaces"
	sysApp "github.com/yourorg/erp-mes-wms-go/internal/modules/system/application"
	sysIntf "github.com/yourorg/erp-mes-wms-go/internal/modules/system/interfaces"
	wmsApp "github.com/yourorg/erp-mes-wms-go/internal/modules/wms/application"
	wmsIntf "github.com/yourorg/erp-mes-wms-go/internal/modules/wms/interfaces"
	"github.com/yourorg/erp-mes-wms-go/internal/pkg/logger"
	"go.uber.org/fx"
)

func main() {
	app := fx.New(
		// Provide dependencies
		fx.Provide(
			config.LoadConfig,
			logger.ProvideLogger,
			telemetry.ProvideTracer,
			telemetry.ProvideMetrics,
			db.ProvideDB,
			cache.ProvideRedis,
			mq.ProvideKafkaWriter,
			mq.ProvideKafkaReader,
			casbin.ProvideEnforcer,
			http.ProvideHTTPServer,
			sysApp.NewRoleService,
			sysApp.NewDictService,
			erpApp.NewMaterialService,
			erpApp.NewSalesOrderService,
			wmsApp.NewInventoryService,
			wmsApp.NewEventSubscriber,
			core.NewIdempotentChecker,
			mesApp.NewProductionService,
			erpIntf.NewMaterialHandler,
			erpIntf.NewSalesOrderHandler,
			wmsIntf.NewInventoryHandler,
			mesIntf.NewProductionHandler,
		),
		// Invoke the route registrations and background workers. 
		fx.Invoke(
			wmsApp.RegisterSubscriberHook,
			sysIntf.RegisterAuthRoutes,
			erpIntf.RegisterERPRoutes,
			wmsIntf.RegisterWMSRoutes,
			mesIntf.RegisterMESRoutes,
		),
	)

	app.Run()
}
