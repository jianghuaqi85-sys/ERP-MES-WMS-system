# ERP-MES-WMS 联动系统

企业级制造业管理系统，实现 ERP（企业资源计划）、MES（制造执行系统）、WMS（仓储管理系统）的全链路联动。

> 核心价值：销售订单确认后自动下发生产工单，生产报工时自动扣减原料库存、增加成品库存并生成溯源记录，发货时自动扣减成品库存——三大系统数据实时联动，消除信息孤岛。

## 系统预览

| 仪表盘                  | 产品管理                  | 生产工单                  |
|:--------------------:|:---------------------:|:---------------------:|
| ![仪表盘](images/1.png) | ![产品管理](images/2.png) | ![生产工单](images/3.png) |
| **BOM 物料清单**         | **销售订单**              | **库存管理**              |
| ![BOM](images/4.png) | ![销售订单](images/5.png) | ![库存](images/6.png)   |
| **供应商**              | **溯源图谱**              |                       |
| ![供应商](images/7.png) | ![溯源](images/8.png)   |                       |

## 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                           │
│                (负载均衡 + HTTPS + 静态资源)                   │
├──────────────────────────────────────────────────────────────┤
│                   前端 SPA (React 19 + TypeScript)             │
│            暗色企业级 UI · TailwindCSS 4 · Framer Motion      │
│         React Flow 溯源图谱 · Recharts 数据图表               │
├───────────┬───────────┬───────────┬───────────┬───────────────┤
│   Auth    │    ERP    │    MES    │    WMS    │ Traceability  │
│   模块    │    模块   │    模块   │    模块   │     模块       │
│           │           │           │           │               │
│ 登录/注册 │ 产品/BOM  │ 工单/报工 │ 物料/库存 │   全链路追溯   │
│ RBAC 权限 │ 销售/采购 │ 工序管理  │ 出入库    │               │
├───────────┴───────────┴───────────┴───────────┴───────────────┤
│                     共享内核 (Shared Kernel)                    │
│  PostgreSQL 18 · Redis 缓存 · JWT 认证 · 审计日志 · 分布式锁  │
└──────────────────────────────────────────────────────────────┘
```

## 核心功能模块

### ERP 模块

- **产品管理**：成品基础数据 CRUD，含编码、名称、价格、单位
- **BOM 物料清单**：定义产品的物料配方，支持多版本管理，一键激活/废弃
- **销售订单**：从下单到发货的全流程管理（草稿 → 确认 → 生产 → 待发货 → 已发货）
- **供应商管理**：供应商信息维护，支持黑名单状态
- **采购订单**：原料采购管理，含明细行和收货跟踪

### MES 模块

- **生产工单**：工单创建、状态流转（计划 → 未开始 → 进行中 → 完成 → 关闭）
- **工序管理**：定义生产步骤和顺序，跟踪每道工序状态
- **生产报工**：核心联动逻辑——扣减原料库存、增加成品库存、自动生成溯源记录

### WMS 模块

- **物料管理**：物料基础数据 CRUD，含安全库存设置
- **库存管理**：实时库存查询、批次管理、库位管理
- **入库/出库**：物料出入库操作，行级锁防并发
- **库存盘点**：盘点调整，自动生成差异变动日志
- **库存变动日志**：所有操作留痕，支持按单据追溯

### 溯源模块

- **全链路追溯**：从成品反查原料批次、生产工单、供应商信息，React Flow 可视化图谱

### 系统模块

- **用户管理**：基于角色的权限控制（RBAC），5 种预设角色
- **操作审计**：所有写操作记录审计日志，含变更前后值
- **仪表盘**：系统数据概览，Recharts 图表展示

## 技术栈

### 后端

| 类别  | 技术                      | 说明                     |
| --- | ----------------------- | ---------------------- |
| 框架  | FastAPI 0.104           | 异步 Python Web 框架       |
| ORM | SQLAlchemy 2.0          | 声明式模型 + 连接池管理          |
| 数据库 | PostgreSQL 18           | 主数据存储                  |
| 缓存  | Redis 5.0               | 缓存 + 分布式锁              |
| 认证  | JWT (python-jose)       | HS256 签名，Token 有效期 24h |
| 密码  | bcrypt + passlib        | 哈希加密                   |
| 迁移  | Alembic                 | 数据库版本管理                |
| 日志  | Loguru                  | 结构化日志，500MB 轮转         |
| 测试  | pytest + pytest-asyncio | 单元测试 + 异步测试            |

### 前端

| 类别   | 技术                      | 说明           |
| ---- | ----------------------- | ------------ |
| 框架   | React 19 + TypeScript 6 | 类型安全的 SPA    |
| 构建   | Vite 8                  | 开发热更新 + 生产构建 |
| UI   | TailwindCSS 4           | 原子化 CSS      |
| 动画   | Framer Motion           | 页面过渡动画       |
| 图表   | Recharts 3.8            | 数据可视化        |
| 图谱   | @xyflow/react 12        | 溯源关系图谱       |
| 虚拟列表 | react-virtuoso          | 大数据量高性能滚动    |
| HTTP | Axios                   | API 请求封装     |
| 路由   | React Router DOM 7      | 客户端路由        |
| 通知   | sonner                  | Toast 通知     |
| 图标   | lucide-react            | 图标库          |

### 部署

- **容器化**：Docker + Docker Compose
- **反向代理**：Nginx（前端静态资源 + API 反向代理）
- **生产配置**：资源限制 + 副本部署 + 健康检查

## 快速开始

### 开发环境

1. **启动基础设施**
   
   ```bash
   docker-compose up -d postgres redis
   ```

2. **启动后端**
   
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   cp .env.example .env  # 修改配置
   alembic upgrade head  # 执行数据库迁移
   python seed.py        # 初始化种子数据
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **启动前端**
   
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **访问系统**
   
   - 前端：http://localhost:5173
   - 后端 API：http://localhost:8000
   - API 文档：http://localhost:8000/docs

### 默认账号

| 用户名      | 密码     | 角色                | 权限范围   |
| -------- | ------ | ----------------- | ------ |
| admin    | 123456 | 管理员 (ADMIN)       | 全部模块   |
| erp_user | 123456 | ERP 用户 (ERP_USER) | ERP 模块 |
| mes_user | 123456 | MES 用户 (MES_USER) | MES 模块 |
| wms_user | 123456 | WMS 用户 (WMS_USER) | WMS 模块 |

### 生产环境

```bash
# 复制并修改生产配置
cp .env.production .env
# 修改 .env 中的密码和密钥

# 启动全栈
docker-compose -f docker-compose.prod.yml up -d --build
```

### 环境变量

| 变量名                           | 默认值            | 说明                            |
| ----------------------------- | -------------- | ----------------------------- |
| `ENVIRONMENT`                 | `development`  | 运行环境：development / production |
| `SECRET_KEY`                  | `CHANGE_ME...` | JWT 签名密钥（生产必须修改）              |
| `POSTGRES_SERVER`             | `localhost`    | 数据库地址                         |
| `POSTGRES_PORT`               | `5434`         | 数据库端口（开发环境映射）                 |
| `POSTGRES_USER`               | `admin`        | 数据库用户                         |
| `POSTGRES_PASSWORD`           | `password`     | 数据库密码                         |
| `POSTGRES_DB`                 | `erp_system`   | 数据库名                          |
| `REDIS_HOST`                  | `localhost`    | Redis 地址                      |
| `REDIS_PORT`                  | `6379`         | Redis 端口                      |
| `REDIS_PASSWORD`              | _(空)_          | Redis 密码（生产环境设置）              |
| `CORS_ORIGINS`                | `["*"]`        | 允许的跨域来源                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440`         | Token 过期时间（分钟）                |

## 数据库表结构

### ER 关系图

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  erp_products│◄───│ erp_sales_   │    │  erp_boms   │
│  (成品)      │    │ orders       │    │  (BOM)      │
│              │    │ (销售订单)    │    │             │
│  id          │    │              │    │  product_id ─┼──► erp_products
│  product_code│    │  product_id ─┼──► │  version    │
│  name        │    │  status      │    │  status     │
│  price       │    └──────────────┘    └──────┬──────┘
│  unit        │                               │
└──────┬───────┘                    ┌───────────┘
       │                            ▼
       │                   ┌──────────────┐
       │                   │ erp_bom_items│    ┌───────────────┐
       │                   │ (BOM 子件)   │    │ wms_materials │
       │                   │              │    │ (物料)        │
       │                   │  material_id ─┼──►│               │
       │                   │  quantity    │    │  material_code│
       │                   └──────────────┘    │  name         │
       │                                       │  safety_stock │
       │                  ┌───────────────┐    └───────┬───────┘
       │                  │ mes_work_     │            │
       │                  │ orders        │            │
       │                  │ (生产工单)    │            │
       │                  │               │            │
       │                  │ product_id ───┼──►         │
       │                  │ sales_order_id│            │
       │                  │ bom_id        │            │
       │                  │ status        │            │
       │                  └───────┬───────┘            │
       │                          │                    │
       │               ┌──────────┘                    │
       │               ▼                               ▼
       │   ┌───────────────────┐          ┌──────────────────┐
       │   │ mes_work_order_   │          │ wms_inventories  │
       │   │ processes         │          │ (库存)           │
       │   │ (工序)            │          │                  │
       │   │                   │          │ material_id      │
       │   │ work_order_id     │          │ product_id       │
       │   │ process_name      │          │ location_code    │
       │   │ sequence          │          │ batch_number     │
       │   └───────────────────┘          │ available_qty    │
       │                                  │ locked_qty       │
       │                                  └────────┬─────────┘
       │                                           │
       │                                  ┌────────┘
       │                                  ▼
       │                      ┌──────────────────────┐
       │                      │ wms_inventory_        │
       │                      │ transactions          │
       │                      │ (库存变动日志)        │
       │                      │                       │
       │                      │ inventory_id          │
       │                      │ transaction_type      │
       │                      │ quantity              │
       │                      └───────────────────────┘
       │
       ▼
┌──────────────────┐     ┌─────────────────────┐
│ traceability_    │     │ erp_purchase_       │
│ records          │     │ orders              │
│ (溯源记录)       │     │ (采购订单)          │
│                  │     │                     │
│ source_type/id   │     │ supplier_id ────────┼──► erp_suppliers
│ target_type/id   │     │ status              │
│ work_order_id    │     └─────────┬───────────┘
│ action_type      │               │
└──────────────────┘     ┌─────────┘
                         ▼
              ┌──────────────────────┐
              │ erp_purchase_order_  │
              │ items                │
              │ (采购明细)           │
              │ material_id          │
              │ quantity / received  │
              └──────────────────────┘

┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ auth_users   │     │ system_audit_logs │     │ wms_warehouse_   │
│ (用户)       │     │ (审计日志)        │     │ locations        │
│              │     │                   │     │ (库位)           │
│ username     │     │ user_id / action  │     │                  │
│ role         │     │ module / resource │     │ warehouse_code   │
│ is_active    │     │ old/new_value     │     │ zone/shelf/layer │
└──────────────┘     └───────────────────┘     └──────────────────┘
```

### 表清单

| 表名                           | 模块           | 说明          |
| ---------------------------- | ------------ | ----------- |
| `auth_users`                 | Auth         | 用户表，RBAC 角色 |
| `erp_products`               | ERP          | 成品表         |
| `erp_boms`                   | ERP          | BOM 物料清单主表  |
| `erp_bom_items`              | ERP          | BOM 子件明细    |
| `erp_sales_orders`           | ERP          | 销售订单        |
| `erp_suppliers`              | ERP          | 供应商         |
| `erp_purchase_orders`        | ERP          | 采购订单        |
| `erp_purchase_order_items`   | ERP          | 采购订单明细      |
| `mes_work_orders`            | MES          | 生产工单        |
| `mes_work_order_processes`   | MES          | 工单工序        |
| `wms_materials`              | WMS          | 物料表         |
| `wms_inventories`            | WMS          | 库存表（行级锁防并发） |
| `wms_inventory_transactions` | WMS          | 库存变动日志      |
| `wms_warehouse_locations`    | WMS          | 库位表         |
| `traceability_records`       | Traceability | 溯源记录        |
| `system_audit_logs`          | System       | 审计日志        |

### 并发控制

系统在关键业务操作中使用 **行级锁**（`SELECT ... FOR UPDATE`）防止并发问题：

- **生产报工**：锁工单 + 锁原料库存 + 锁成品库存，防止报工并发导致库存超扣
- **出库操作**：锁库存记录，防止并发出库导致负库存
- **库存盘点**：锁库存记录，防止盘点期间发生出入库
- **分布式锁**：Redis 实现的 `DistributedLock`，用于跨进程互斥

## API 端点清单

### Auth `/api/v1/auth`

| Method | Path        | 说明       |
| ------ | ----------- | -------- |
| POST   | `/login`    | 登录       |
| POST   | `/register` | 注册       |
| GET    | `/me`       | 获取当前用户信息 |

### ERP `/api/v1/erp`

| Method         | Path                         | 说明          |
| -------------- | ---------------------------- | ----------- |
| GET/POST       | `/products`                  | 产品列表/创建     |
| GET/PUT/DELETE | `/products/{id}`             | 产品详情/编辑/删除  |
| GET/POST       | `/boms`                      | BOM 列表/创建   |
| GET            | `/boms/{id}`                 | BOM 详情      |
| POST           | `/boms/{id}/activate`        | 激活 BOM      |
| GET/POST       | `/sales-orders`              | 销售订单列表/创建   |
| GET/PUT        | `/sales-orders/{id}`         | 订单详情/编辑     |
| POST           | `/sales-orders/{id}/confirm` | 确认订单        |
| POST           | `/sales-orders/{id}/ship`    | 发货          |
| POST           | `/sales-orders/{id}/cancel`  | 取消          |
| GET/POST       | `/suppliers`                 | 供应商列表/创建    |
| GET/PUT/DELETE | `/suppliers/{id}`            | 供应商详情/编辑/删除 |
| GET/POST       | `/purchase-orders`           | 采购订单列表/创建   |
| GET            | `/purchase-orders/{id}`      | 采购订单详情      |

### MES `/api/v1/mes`

| Method   | Path                          | 说明   |
| -------- | ----------------------------- | ---- |
| GET      | `/work-orders`                | 工单列表 |
| GET      | `/work-orders/{id}`           | 工单详情 |
| POST     | `/work-orders/{id}/start`     | 开始生产 |
| POST     | `/work-orders/{id}/report`    | 生产报工 |
| POST     | `/work-orders/{id}/complete`  | 完成工单 |
| POST     | `/work-orders/{id}/close`     | 关闭工单 |
| GET/POST | `/work-orders/{id}/processes` | 工序管理 |

### WMS `/api/v1/wms`

| Method         | Path                      | 说明         |
| -------------- | ------------------------- | ---------- |
| GET/POST       | `/materials`              | 物料列表/创建    |
| GET/PUT/DELETE | `/materials/{id}`         | 物料详情/编辑/删除 |
| GET            | `/inventory`              | 库存查询       |
| POST           | `/materials/receive`      | 入库         |
| POST           | `/materials/dispatch`     | 出库         |
| POST           | `/inventory/stocktake`    | 库存盘点       |
| GET            | `/inventory/transactions` | 库存变动日志     |
| GET/POST       | `/locations`              | 库位管理       |

### System `/api/v1/system`

| Method | Path               | 说明    |
| ------ | ------------------ | ----- |
| GET    | `/dashboard/stats` | 仪表盘统计 |
| GET    | `/audit-logs`      | 操作日志  |
| GET    | `/users`           | 用户管理  |

## 项目结构

```
ERP–MES–WMS 联动的系统/
├── docker-compose.yml              # 开发环境
├── docker-compose.prod.yml         # 生产环境（资源限制 + 副本部署）
├── images/                         # 系统截图
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                    # 数据库迁移
│   │   ├── env.py                  # 迁移环境配置
│   │   └── versions/               # 迁移版本文件
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口 + 中间件 + 路由注册
│   │   ├── core/                   # 共享内核
│   │   │   ├── config.py           # Pydantic Settings 配置管理
│   │   │   ├── database.py         # SQLAlchemy 引擎 + 会话工厂
│   │   │   ├── models.py           # TimestampMixin 时间戳基类
│   │   │   ├── redis.py            # Redis 缓存 + 分布式锁
│   │   │   └── constants.py        # 业务状态常量（防魔法字符串）
│   │   └── apps/                   # 业务模块（按领域划分）
│   │       ├── auth/               # 认证授权
│   │       │   ├── models.py       #   User 模型
│   │       │   ├── router.py       #   登录/注册/获取用户
│   │       │   ├── schemas.py      #   Pydantic 请求/响应模型
│   │       │   ├── dependencies.py #   RBAC 依赖注入（require_roles）
│   │       │   └── utils.py        #   JWT + 密码哈希工具
│   │       ├── erp/                # ERP 模块
│   │       │   ├── models.py       #   Product/BOM/SalesOrder/Supplier/PurchaseOrder
│   │       │   ├── router.py       #   RESTful API 路由
│   │       │   ├── schemas.py      #   请求/响应模型
│   │       │   └── services.py     #   业务逻辑（订单确认→自动创建工单）
│   │       ├── mes/                # MES 模块
│   │       │   ├── models.py       #   WorkOrder/WorkOrderProcess
│   │       │   ├── router.py       #   工单状态流转 API
│   │       │   ├── schemas.py      #   请求/响应模型
│   │       │   └── services.py     #   报工核心逻辑（三系统联动）
│   │       ├── wms/                # WMS 模块
│   │       │   ├── models.py       #   Material/Inventory/Transaction/Location
│   │       │   ├── router.py       #   物料/库存 API
│   │       │   ├── schemas.py      #   请求/响应模型
│   │       │   └── services.py     #   出入库 + 盘点逻辑
│   │       ├── traceability/       # 溯源模块
│   │       │   ├── models.py       #   TraceabilityRecord
│   │       │   └── router.py       #   溯源查询 API
│   │       └── system/             # 系统模块
│   │           ├── models.py       #   AuditLog
│   │           ├── router.py       #   仪表盘/审计日志/用户管理
│   │           └── schemas.py      #   请求/响应模型
│   └── seed.py                     # 种子数据初始化
└── frontend/
    ├── Dockerfile
    ├── nginx.conf                  # Nginx 配置（SPA 路由 + API 代理）
    ├── package.json
    └── src/
        ├── App.tsx                 # 路由配置 + 鉴权守卫
        ├── main.tsx                # React 入口
        ├── index.css               # 全局样式 + TailwindCSS
        ├── components/             # 公共组件
        │   ├── Layout.tsx          #   侧边栏布局 + 导航
        │   ├── InfoPanel.tsx        #   信息面板组件
        │   └── TraceabilityGraph.tsx#   溯源图谱（React Flow）
        ├── pages/                  # 页面组件
        │   ├── Login.tsx           #   登录页
        │   ├── Dashboard.tsx       #   仪表盘（数据概览 + 图表）
        │   ├── ProductList.tsx     #   产品管理
        │   ├── BOMList.tsx         #   BOM 物料清单
        │   ├── SalesOrderList.tsx  #   销售订单
        │   ├── SupplierList.tsx    #   供应商管理
        │   ├── PurchaseOrderList.tsx#  采购订单
        │   ├── WorkOrderList.tsx   #   生产工单
        │   └── MaterialList.tsx    #   库存管理
        ├── utils/                  # 工具函数
        │   └── api.ts             #   Axios 实例 + 请求/响应拦截器
        └── assets/                 # 静态资源
```

## 核心业务流程

### 销售到交付（Order-to-Delivery）

```
创建销售订单 (DRAFT)
    │
    ▼
确认订单 ──────────── 自动创建生产工单 (PLANNED)
    │                     │
    │                     ▼
    │               开始生产 (IN_PROGRESS)
    │                     │
    │                     ▼
    │               生产报工 ───┬── 扣减原料库存 (WMS)
    │                          ├── 增加成品库存 (WMS)
    │                          └── 写入溯源记录 (Traceability)
    │                     │
    │                     ▼
    │               完成工单 (COMPLETED) → 订单状态变为 READY_TO_SHIP
    │                     │
    ▼                     ▼
发货 (SHIPPED) ──── 扣减成品库存 (WMS)
```

### 采购到付款（Procure-to-Pay）

```
创建采购订单 (DRAFT)
    │
    ▼
确认订单 (CONFIRMED)
    │
    ▼
采购入库 ──── 增加原料库存 (WMS) + 记录变动日志
    │
    ▼
收货完成 (RECEIVED)
```

### 全链路追溯（Full Traceability）

```
成品条码/批次号
    │
    ▼
溯源记录 (traceability_records)
    │
    ├──► 生产工单信息 (mes_work_orders)
    │        │
    │        └──► 工单工序 (mes_work_order_processes)
    │
    ├──► 原料批次信息 (source_barcode)
    │        │
    │        └──► 物料信息 (wms_materials)
    │
    └──► 供应商信息 (通过采购订单关联)
```

### 前端路由

| 路径                     | 页面                | 说明        |
| ---------------------- | ----------------- | --------- |
| `/login`               | Login             | 登录页（无需鉴权） |
| `/`                    | Dashboard         | 仪表盘，数据概览  |
| `/erp/products`        | ProductList       | 产品管理      |
| `/erp/boms`            | BOMList           | BOM 物料清单  |
| `/erp/sales-orders`    | SalesOrderList    | 销售订单      |
| `/erp/suppliers`       | SupplierList      | 供应商管理     |
| `/erp/purchase-orders` | PurchaseOrderList | 采购订单      |
| `/mes/work-orders`     | WorkOrderList     | 生产工单      |
| `/wms/inventory`       | MaterialList      | 库存管理      |

> 所有业务路由均需 JWT Token，未登录自动跳转 `/login`。

## 开发规范

### 代码风格

- **Python**：snake_case 命名，完整类型注解，函数 < 50 行
- **TypeScript**：camelCase 命名，严格类型，组件 PascalCase
- **Git**：约定式提交（feat/fix/refactor/docs/test）

### API 设计

- RESTful 风格，统一 `/api/v1` 前缀
- 统一错误响应格式：`{"code": 50000, "message": "...", "details": "..."}`
- JWT Bearer Token 认证
- RBAC 权限控制（`require_roles` 依赖注入）
- 生产环境隐藏内部异常详情

### 数据库

- SQLAlchemy 2.0 声明式 ORM
- Alembic 迁移管理，禁止手动改表
- 连接池：pool_size=10, max_overflow=20, 30 分钟回收
- 行级锁（`SELECT ... FOR UPDATE`）防并发
- `TimestampMixin` 统一 created_at / updated_at

### 模块结构

每个业务模块遵循统一的四文件结构：

```
apps/<module>/
├── models.py     # SQLAlchemy 模型定义
├── schemas.py    # Pydantic 请求/响应模型
├── router.py     # FastAPI 路由定义
└── services.py   # 业务逻辑（可选）
```

## License

MIT
