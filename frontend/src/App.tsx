import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Layout } from './components/Layout';
import { MaterialList } from './pages/MaterialList';
import { WorkOrderList } from './pages/WorkOrderList';
import { ProductList } from './pages/ProductList';
import { SalesOrderList } from './pages/SalesOrderList';
import { SupplierList } from './pages/SupplierList';
import { PurchaseOrderList } from './pages/PurchaseOrderList';
import { BOMList } from './pages/BOMList';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* 使用 Layout 包裹需要鉴权的页面 */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />

          {/* ERP 模块 */}
          <Route path="erp/products" element={<ProductList />} />
          <Route path="erp/boms" element={<BOMList />} />
          <Route path="erp/sales-orders" element={<SalesOrderList />} />
          <Route path="erp/suppliers" element={<SupplierList />} />
          <Route path="erp/purchase-orders" element={<PurchaseOrderList />} />

          {/* MES 模块 */}
          <Route path="mes/work-orders" element={<WorkOrderList />} />

          {/* WMS 模块 */}
          <Route path="wms/inventory" element={<MaterialList />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
