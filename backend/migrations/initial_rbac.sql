-- RBAC 初始化 SQL 脚本
-- 适用于 PostgreSQL 部署时直接执行

-- 1. 插入默认权限 (Permissions)
INSERT INTO auth_permissions (name, description, created_at, updated_at) VALUES
('admin:*', 'Administrator all permissions', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('erp:read', 'Read ERP data', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('erp:write', 'Write/Modify ERP data', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('mes:read', 'Read MES data', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('mes:write', 'Write/Modify MES data', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('wms:read', 'Read WMS data', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('wms:write', 'Write/Modify WMS data', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (name) DO NOTHING;

-- 2. 插入默认角色 (Roles)
INSERT INTO auth_roles (name, description, created_at, updated_at) VALUES
('ADMIN', 'System Administrator', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('ERP_USER', 'ERP Operator', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('MES_USER', 'MES Operator', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('WMS_USER', 'WMS Operator', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (name) DO NOTHING;

-- 3. 关联角色与权限 (Role-Permission Associations)
-- 我们使用 SELECT 子查询确保获取正确的自增 ID

-- ADMIN 关联 admin:*
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM auth_roles r, auth_permissions p
WHERE r.name = 'ADMIN' AND p.name = 'admin:*'
ON CONFLICT DO NOTHING;

-- ERP_USER 关联 erp:read, erp:write
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM auth_roles r, auth_permissions p
WHERE r.name = 'ERP_USER' AND p.name IN ('erp:read', 'erp:write')
ON CONFLICT DO NOTHING;

-- MES_USER 关联 mes:read, mes:write
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM auth_roles r, auth_permissions p
WHERE r.name = 'MES_USER' AND p.name IN ('mes:read', 'mes:write')
ON CONFLICT DO NOTHING;

-- WMS_USER 关联 wms:read, wms:write
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM auth_roles r, auth_permissions p
WHERE r.name = 'WMS_USER' AND p.name IN ('wms:read', 'wms:write')
ON CONFLICT DO NOTHING;
