import React, { useEffect, useState } from 'react';
import { FileText, Plus, Search, Check } from 'lucide-react';
import api from '../utils/axios';

interface BOM {
  id: number;
  product_id: number;
  version: string;
  is_default: boolean;
  status: string;
  remark: string;
  items: BOMItem[];
}

interface BOMItem {
  id: number;
  material_id: number;
  quantity: number;
  unit: string;
}

const statusMap: Record<string, { label: string; color: string }> = {
  DRAFT: { label: '草稿', color: 'bg-gray-500/20 text-gray-400 border-gray-500/50' },
  ACTIVE: { label: '已激活', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' },
  OBSOLETE: { label: '已废弃', color: 'bg-red-500/20 text-red-400 border-red-500/50' },
};

export const BOMList: React.FC = () => {
  const [boms, setBoms] = useState<BOM[]>([]);
  const [loading, setLoading] = useState(true);
  const [productId, setProductId] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ product_id: 0, version: '1.0', remark: '', items: [{ material_id: 0, quantity: 1, unit: 'pcs' }] });

  const fetchBOMs = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (productId) params.product_id = productId;
      const res = await api.get('/api/v1/erp/boms', { params });
      setBoms(res.data.items);
    } catch (e) {
      console.error('获取 BOM 列表失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBOMs(); }, []);

  const handleActivate = async (id: number) => {
    if (!confirm('激活此 BOM？同产品的其他 BOM 将被废弃。')) return;
    try {
      await api.post(`/api/v1/erp/boms/${id}/activate`);
      fetchBOMs();
    } catch (e: any) {
      alert(e.response?.data?.detail || '激活失败');
    }
  };

  const handleCreate = async () => {
    try {
      await api.post('/api/v1/erp/boms', formData);
      setShowForm(false);
      fetchBOMs();
    } catch (e: any) {
      alert(e.response?.data?.detail || '创建失败');
    }
  };

  const addItem = () => {
    setFormData({ ...formData, items: [...formData.items, { material_id: 0, quantity: 1, unit: 'pcs' }] });
  };

  const removeItem = (index: number) => {
    setFormData({ ...formData, items: formData.items.filter((_, i) => i !== index) });
  };

  const updateItem = (index: number, field: string, value: any) => {
    const items = [...formData.items];
    items[index] = { ...items[index], [field]: value };
    setFormData({ ...formData, items });
  };

  return (
    <div className="p-8 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <FileText className="text-teal-400" />
            BOM 物料清单
          </h2>
          <p className="text-gray-400 text-sm mt-1">管理产品的物料配方</p>
        </div>
        <button onClick={() => setShowForm(true)} className="bg-teal-500/20 text-teal-400 border border-teal-500/50 hover:bg-teal-500/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Plus className="w-4 h-4" /> 新增 BOM
        </button>
      </div>

      <div className="mb-6 flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="number" value={productId} onChange={e => setProductId(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetchBOMs()} placeholder="按产品 ID 筛选..." className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-teal-500/50" />
        </div>
        <button onClick={fetchBOMs} className="bg-white/5 border border-white/10 hover:bg-white/10 px-4 py-2 rounded-lg text-sm text-gray-300 transition-colors">筛选</button>
      </div>

      <div className="glass-panel flex-1 rounded-2xl overflow-y-auto border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
              <th className="p-4 font-medium">ID</th>
              <th className="p-4 font-medium">产品 ID</th>
              <th className="p-4 font-medium">版本</th>
              <th className="p-4 font-medium">子件数</th>
              <th className="p-4 font-medium">状态</th>
              <th className="p-4 font-medium">默认</th>
              <th className="p-4 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {boms.map(b => (
              <tr key={b.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                <td className="p-4 text-gray-300">#{b.id}</td>
                <td className="p-4 font-mono text-teal-400">PRD-{b.product_id}</td>
                <td className="p-4 text-gray-300">{b.version}</td>
                <td className="p-4 text-gray-300">{b.items?.length || 0}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-1 rounded-md border ${statusMap[b.status]?.color || 'bg-gray-500/20 text-gray-400'}`}>
                    {statusMap[b.status]?.label || b.status}
                  </span>
                </td>
                <td className="p-4">{b.is_default && <Check className="w-4 h-4 text-emerald-400" />}</td>
                <td className="p-4">
                  {b.status === 'DRAFT' && (
                    <button onClick={() => handleActivate(b.id)} className="text-teal-400 hover:text-teal-300 text-xs underline transition-colors">激活</button>
                  )}
                </td>
              </tr>
            ))}
            {boms.length === 0 && (
              <tr><td colSpan={7} className="p-8 text-center text-gray-500">暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-lg my-8">
            <h3 className="text-lg font-bold mb-4">新增 BOM</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">产品 ID</label>
                  <input type="number" value={formData.product_id} onChange={e => setFormData({...formData, product_id: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-teal-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">版本</label>
                  <input value={formData.version} onChange={e => setFormData({...formData, version: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-teal-500/50" />
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">子件明细</label>
                {formData.items.map((item, idx) => (
                  <div key={idx} className="flex gap-2 mb-2">
                    <input type="number" placeholder="物料 ID" value={item.material_id || ''} onChange={e => updateItem(idx, 'material_id', Number(e.target.value))} className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-teal-500/50" />
                    <input type="number" placeholder="用量" value={item.quantity || ''} onChange={e => updateItem(idx, 'quantity', Number(e.target.value))} className="w-24 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-teal-500/50" />
                    <input placeholder="单位" value={item.unit} onChange={e => updateItem(idx, 'unit', e.target.value)} className="w-20 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-teal-500/50" />
                    {formData.items.length > 1 && (
                      <button onClick={() => removeItem(idx)} className="text-red-400 hover:text-red-300 px-2">✕</button>
                    )}
                  </div>
                ))}
                <button onClick={addItem} className="text-teal-400 hover:text-teal-300 text-sm underline">+ 添加子件</button>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">备注</label>
                <textarea value={formData.remark} onChange={e => setFormData({...formData, remark: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-teal-500/50 h-16 resize-none" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">取消</button>
              <button onClick={handleCreate} className="bg-teal-500/20 text-teal-400 border border-teal-500/50 hover:bg-teal-500/30 px-4 py-2 rounded-lg transition-colors">创建</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
