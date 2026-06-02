import React, { useEffect, useState } from 'react';
import { Truck, Plus, Search } from 'lucide-react';
import api from '../utils/axios';

interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_id: number;
  total_amount: number;
  status: string;
  remark: string;
}

const statusMap: Record<string, { label: string; color: string }> = {
  DRAFT: { label: '草稿', color: 'bg-gray-500/20 text-gray-400 border-gray-500/50' },
  PENDING: { label: '待确认', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' },
  CONFIRMED: { label: '已确认', color: 'bg-blue-500/20 text-blue-400 border-blue-500/50' },
  PARTIALLY_RECEIVED: { label: '部分收货', color: 'bg-purple-500/20 text-purple-400 border-purple-500/50' },
  RECEIVED: { label: '已收货', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' },
  CANCELLED: { label: '已取消', color: 'bg-red-500/20 text-red-400 border-red-500/50' },
};

export const PurchaseOrderList: React.FC = () => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/erp/purchase-orders');
      setOrders(res.data.items);
    } catch (e) {
      console.error('获取采购订单失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, []);

  return (
    <div className="p-8 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Truck className="text-cyan-400" />
            采购订单
          </h2>
          <p className="text-gray-400 text-sm mt-1">管理原料采购订单</p>
        </div>
      </div>

      <div className="glass-panel flex-1 rounded-2xl overflow-y-auto border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
              <th className="p-4 font-medium">采购单号</th>
              <th className="p-4 font-medium">供应商 ID</th>
              <th className="p-4 font-medium">总金额</th>
              <th className="p-4 font-medium">状态</th>
              <th className="p-4 font-medium">备注</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => (
              <tr key={o.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                <td className="p-4 font-mono text-cyan-400">{o.po_number}</td>
                <td className="p-4 text-gray-300">{o.supplier_id}</td>
                <td className="p-4 text-emerald-400">¥{o.total_amount || '-'}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-1 rounded-md border ${statusMap[o.status]?.color || 'bg-gray-500/20 text-gray-400'}`}>
                    {statusMap[o.status]?.label || o.status}
                  </span>
                </td>
                <td className="p-4 text-gray-500 max-w-xs truncate">{o.remark || '-'}</td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr><td colSpan={5} className="p-8 text-center text-gray-500">暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
