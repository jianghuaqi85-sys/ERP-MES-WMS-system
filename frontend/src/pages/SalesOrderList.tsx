import React, { useEffect, useState } from 'react';
import { ShoppingCart, Plus, Search, Check, Truck, X, Edit } from 'lucide-react';
import api from '../utils/axios';

interface SalesOrder {
  id: number;
  order_number: string;
  customer_name: string;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_amount: number;
  status: string;
}

const statusMap: Record<string, { label: string; color: string }> = {
  DRAFT: { label: '草稿', color: 'bg-gray-500/20 text-gray-400 border-gray-500/50' },
  PENDING: { label: '待确认', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' },
  CONFIRMED: { label: '已确认', color: 'bg-blue-500/20 text-blue-400 border-blue-500/50' },
  IN_PRODUCTION: { label: '生产中', color: 'bg-purple-500/20 text-purple-400 border-purple-500/50' },
  READY_TO_SHIP: { label: '待发货', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' },
  SHIPPED: { label: '已发货', color: 'bg-green-500/20 text-green-400 border-green-500/50' },
  CANCELLED: { label: '已取消', color: 'bg-red-500/20 text-red-400 border-red-500/50' },
};

export const SalesOrderList: React.FC = () => {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState(new URLSearchParams(window.location.search).get('keyword') || '');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ customer_name: '', product_id: 0, quantity: 1, unit_price: 0, remark: '' });

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/erp/sales-orders', { params: { keyword } });
      setOrders(res.data.items);
    } catch (e) {
      console.error('获取销售订单失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, []);

  const openCreate = () => {
    setFormData({ customer_name: '', product_id: 0, quantity: 1, unit_price: 0, remark: '' });
    setEditingId(null);
    setShowForm(true);
  };

  const openEdit = (o: SalesOrder) => {
    setFormData({ customer_name: o.customer_name, product_id: o.product_id, quantity: o.quantity, unit_price: o.unit_price, remark: '' });
    setEditingId(o.id);
    setShowForm(true);
  };

  const handleSave = async () => {
    try {
      if (editingId) {
        await api.put(`/api/v1/erp/sales-orders/${editingId}`, formData);
      } else {
        await api.post('/api/v1/erp/sales-orders', formData);
      }
      setShowForm(false);
      fetchOrders();
    } catch (e: any) {
      alert(e.response?.data?.detail || '保存失败');
    }
  };

  const handleConfirm = async (id: number) => {
    if (!confirm('确认此订单？将自动创建生产工单。')) return;
    try {
      await api.post(`/api/v1/erp/sales-orders/${id}/confirm`);
      fetchOrders();
    } catch (e: any) {
      alert(e.response?.data?.detail || '确认失败');
    }
  };

  const handleShip = async (id: number) => {
    if (!confirm('确认发货？将扣减成品库存。')) return;
    try {
      await api.post(`/api/v1/erp/sales-orders/${id}/ship`);
      fetchOrders();
    } catch (e: any) {
      alert(e.response?.data?.detail || '发货失败');
    }
  };

  const handleCancel = async (id: number) => {
    if (!confirm('确定要取消此订单吗？')) return;
    try {
      await api.post(`/api/v1/erp/sales-orders/${id}/cancel`);
      fetchOrders();
    } catch (e: any) {
      alert(e.response?.data?.detail || '取消失败');
    }
  };

  return (
    <div className="p-8 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <ShoppingCart className="text-purple-400" />
            销售订单
          </h2>
          <p className="text-gray-400 text-sm mt-1">管理客户销售订单</p>
        </div>
        <button onClick={openCreate} className="bg-purple-500/20 text-purple-400 border border-purple-500/50 hover:bg-purple-500/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Plus className="w-4 h-4" /> 新增订单
        </button>
      </div>

      <div className="mb-6 flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="text" value={keyword} onChange={e => setKeyword(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetchOrders()} placeholder="搜索订单号或客户名..." className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500/50" />
        </div>
        <button onClick={fetchOrders} className="bg-white/5 border border-white/10 hover:bg-white/10 px-4 py-2 rounded-lg text-sm text-gray-300 transition-colors">搜索</button>
      </div>

      <div className="glass-panel flex-1 rounded-2xl overflow-y-auto border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
              <th className="p-4 font-medium">订单号</th>
              <th className="p-4 font-medium">客户</th>
              <th className="p-4 font-medium">数量</th>
              <th className="p-4 font-medium">金额</th>
              <th className="p-4 font-medium">状态</th>
              <th className="p-4 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => (
              <tr key={o.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                <td className="p-4 font-mono text-purple-400">{o.order_number}</td>
                <td className="p-4 text-gray-200">{o.customer_name}</td>
                <td className="p-4 text-gray-300">{o.quantity}</td>
                <td className="p-4 text-emerald-400">¥{o.total_amount || '-'}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-1 rounded-md border ${statusMap[o.status]?.color || 'bg-gray-500/20 text-gray-400'}`}>
                    {statusMap[o.status]?.label || o.status}
                  </span>
                </td>
                <td className="p-4 flex gap-2">
                  <button onClick={() => openEdit(o)} className="text-blue-400 hover:text-blue-300 transition-colors" title="编辑">
                    <Edit className="w-4 h-4" />
                  </button>
                  {o.status === 'DRAFT' && (
                    <>
                      <button onClick={() => handleConfirm(o.id)} className="text-blue-400 hover:text-blue-300 transition-colors" title="确认"><Check className="w-4 h-4" /></button>
                      <button onClick={() => handleCancel(o.id)} className="text-red-400 hover:text-red-300 transition-colors" title="取消"><X className="w-4 h-4" /></button>
                    </>
                  )}
                  {o.status === 'READY_TO_SHIP' && (
                    <button onClick={() => handleShip(o.id)} className="text-emerald-400 hover:text-emerald-300 transition-colors" title="发货"><Truck className="w-4 h-4" /></button>
                  )}
                </td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr><td colSpan={6} className="p-8 text-center text-gray-500">暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">{editingId ? '编辑销售订单' : '新增销售订单'}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">客户名称</label>
                <input value={formData.customer_name} onChange={e => setFormData({...formData, customer_name: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500/50" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">产品 ID</label>
                <input type="number" value={formData.product_id} onChange={e => setFormData({...formData, product_id: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500/50" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">数量</label>
                  <input type="number" value={formData.quantity} onChange={e => setFormData({...formData, quantity: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">单价</label>
                  <input type="number" value={formData.unit_price} onChange={e => setFormData({...formData, unit_price: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500/50" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">取消</button>
              <button onClick={handleSave} className="bg-purple-500/20 text-purple-400 border border-purple-500/50 hover:bg-purple-500/30 px-4 py-2 rounded-lg transition-colors">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
