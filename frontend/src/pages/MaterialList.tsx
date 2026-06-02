import React, { useEffect, useState } from 'react';
import { Database, Plus, Search, ArrowDownToLine, ArrowUpFromLine, Trash2 } from 'lucide-react';
import api from '../utils/axios';

interface Material {
  id: number;
  material_code: string;
  name: string;
  unit: string;
  category: string;
  safety_stock: number;
}

interface Inventory {
  id: number;
  material_id: number;
  product_id: number;
  location_code: string;
  batch_number: string;
  available_qty: number;
  locked_qty: number;
}

export const MaterialList: React.FC = () => {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState(new URLSearchParams(window.location.search).get('keyword') || '');
  const [tab, setTab] = useState<'materials' | 'inventory'>('materials');
  const [showForm, setShowForm] = useState(false);
  const [showReceive, setShowReceive] = useState(false);
  const [formData, setFormData] = useState({ material_code: '', name: '', unit: 'pcs', category: '', safety_stock: 0 });
  const [receiveForm, setReceiveForm] = useState({ material_id: 0, quantity: 1, location_code: '', batch_number: '' });

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/wms/materials', { params: { keyword } });
      setMaterials(res.data.items);
    } catch (e) {
      console.error('获取物料列表失败', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/wms/inventory');
      setInventory(res.data.items);
    } catch (e) {
      console.error('获取库存失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tab === 'materials') fetchMaterials();
    else fetchInventory();
  }, [tab]);

  const handleCreateMaterial = async () => {
    try {
      await api.post('/api/v1/wms/materials', formData);
      setShowForm(false);
      setFormData({ material_code: '', name: '', unit: 'pcs', category: '', safety_stock: 0 });
      fetchMaterials();
    } catch (e: any) {
      alert(e.response?.data?.detail || '创建失败');
    }
  };

  const handleDeleteMaterial = async (id: number) => {
    if (!confirm('确定要删除此物料吗？')) return;
    try {
      await api.delete(`/api/v1/wms/materials/${id}`);
      fetchMaterials();
    } catch (e: any) {
      alert(e.response?.data?.detail || '删除失败');
    }
  };

  const handleReceive = async () => {
    try {
      await api.post('/api/v1/wms/materials/receive', receiveForm);
      setShowReceive(false);
      setReceiveForm({ material_id: 0, quantity: 1, location_code: '', batch_number: '' });
      if (tab === 'inventory') fetchInventory();
      alert('入库成功');
    } catch (e: any) {
      alert(e.response?.data?.detail || '入库失败');
    }
  };

  return (
    <div className="p-8 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Database className="text-amber-400" />
            仓储管理
          </h2>
          <p className="text-gray-400 text-sm mt-1">管理物料基础数据与库存</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => setShowReceive(true)} className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <ArrowDownToLine className="w-4 h-4" /> 入库
          </button>
          <button onClick={() => setShowForm(true)} className="bg-amber-500/20 text-amber-400 border border-amber-500/50 hover:bg-amber-500/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus className="w-4 h-4" /> 新增物料
          </button>
        </div>
      </div>

      {/* Tab 切换 */}
      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('materials')} className={`px-4 py-2 rounded-lg text-sm transition-colors ${tab === 'materials' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          物料数据
        </button>
        <button onClick={() => setTab('inventory')} className={`px-4 py-2 rounded-lg text-sm transition-colors ${tab === 'inventory' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'}`}>
          库存台账
        </button>
      </div>

      {/* 搜索栏 */}
      {tab === 'materials' && (
        <div className="mb-6 flex gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input type="text" value={keyword} onChange={e => setKeyword(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetchMaterials()} placeholder="搜索物料编码或名称..." className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-amber-500/50" />
          </div>
          <button onClick={fetchMaterials} className="bg-white/5 border border-white/10 hover:bg-white/10 px-4 py-2 rounded-lg text-sm text-gray-300 transition-colors">搜索</button>
        </div>
      )}

      {/* 表格 */}
      <div className="glass-panel flex-1 rounded-2xl overflow-y-auto border border-white/10">
        {tab === 'materials' ? (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
                <th className="p-4 font-medium">物料编码</th>
                <th className="p-4 font-medium">名称</th>
                <th className="p-4 font-medium">单位</th>
                <th className="p-4 font-medium">分类</th>
                <th className="p-4 font-medium">安全库存</th>
                <th className="p-4 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {materials.map(m => (
                <tr key={m.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                  <td className="p-4 font-mono text-amber-400">{m.material_code}</td>
                  <td className="p-4 text-gray-200">{m.name}</td>
                  <td className="p-4 text-gray-400">{m.unit}</td>
                  <td className="p-4 text-gray-400">{m.category || '-'}</td>
                  <td className="p-4 text-gray-300">{m.safety_stock}</td>
                  <td className="p-4">
                    <button onClick={() => handleDeleteMaterial(m.id)} className="text-red-400 hover:text-red-300 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {materials.length === 0 && (
                <tr><td colSpan={6} className="p-8 text-center text-gray-500">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
                <th className="p-4 font-medium">库存 ID</th>
                <th className="p-4 font-medium">物料/产品 ID</th>
                <th className="p-4 font-medium">库位</th>
                <th className="p-4 font-medium">批次号</th>
                <th className="p-4 font-medium">可用库存</th>
                <th className="p-4 font-medium">锁定库存</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map(inv => (
                <tr key={inv.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                  <td className="p-4 text-gray-300">#{inv.id}</td>
                  <td className="p-4 font-mono text-amber-400">
                    {inv.material_id ? `MAT-${inv.material_id}` : `PRD-${inv.product_id}`}
                  </td>
                  <td className="p-4 text-gray-300">{inv.location_code}</td>
                  <td className="p-4 text-gray-400">{inv.batch_number || '-'}</td>
                  <td className="p-4 font-bold text-emerald-400">{inv.available_qty}</td>
                  <td className="p-4 text-gray-500">{inv.locked_qty}</td>
                </tr>
              ))}
              {inventory.length === 0 && (
                <tr><td colSpan={6} className="p-8 text-center text-gray-500">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* 新增物料弹窗 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">新增物料</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">物料编码</label>
                  <input value={formData.material_code} onChange={e => setFormData({...formData, material_code: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-amber-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">名称</label>
                  <input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-amber-500/50" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">单位</label>
                  <input value={formData.unit} onChange={e => setFormData({...formData, unit: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-amber-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">分类</label>
                  <input value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-amber-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">安全库存</label>
                  <input type="number" value={formData.safety_stock} onChange={e => setFormData({...formData, safety_stock: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-amber-500/50" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">取消</button>
              <button onClick={handleCreateMaterial} className="bg-amber-500/20 text-amber-400 border border-amber-500/50 hover:bg-amber-500/30 px-4 py-2 rounded-lg transition-colors">创建</button>
            </div>
          </div>
        </div>
      )}

      {/* 入库弹窗 */}
      {showReceive && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">物料入库</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">物料 ID</label>
                <input type="number" value={receiveForm.material_id || ''} onChange={e => setReceiveForm({...receiveForm, material_id: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500/50" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">入库数量</label>
                  <input type="number" value={receiveForm.quantity} onChange={e => setReceiveForm({...receiveForm, quantity: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">库位编码</label>
                  <input value={receiveForm.location_code} onChange={e => setReceiveForm({...receiveForm, location_code: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500/50" />
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">批次号（可选）</label>
                <input value={receiveForm.batch_number} onChange={e => setReceiveForm({...receiveForm, batch_number: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500/50" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowReceive(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">取消</button>
              <button onClick={handleReceive} className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-500/30 px-4 py-2 rounded-lg transition-colors">确认入库</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
