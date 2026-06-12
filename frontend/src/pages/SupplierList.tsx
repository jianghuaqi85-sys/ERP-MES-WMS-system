import React, { useEffect, useState } from 'react';
import { Users, Plus, Search, Trash2, Edit } from 'lucide-react';
import api from '../utils/axios';

interface Supplier {
  id: number;
  code: string;
  name: string;
  contact_person: string;
  phone: string;
  email: string;
  status: string;
}

export const SupplierList: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState(new URLSearchParams(window.location.search).get('keyword') || '');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ code: '', name: '', contact_person: '', phone: '', email: '', address: '' });

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/erp/suppliers', { params: { keyword } });
      setSuppliers(res.data.items);
    } catch (e) {
      console.error('获取供应商列表失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSuppliers(); }, []);

  const openCreate = () => {
    setFormData({ code: '', name: '', contact_person: '', phone: '', email: '', address: '' });
    setEditingId(null);
    setShowForm(true);
  };

  const openEdit = (s: Supplier) => {
    setFormData({ code: s.code, name: s.name, contact_person: s.contact_person || '', phone: s.phone || '', email: s.email || '', address: '' });
    setEditingId(s.id);
    setShowForm(true);
  };

  const handleSave = async () => {
    try {
      if (editingId) {
        await api.put(`/api/v1/erp/suppliers/${editingId}`, formData);
      } else {
        await api.post('/api/v1/erp/suppliers', formData);
      }
      setShowForm(false);
      fetchSuppliers();
    } catch (e: any) {
      alert(e.response?.data?.detail || '保存失败');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此供应商吗？')) return;
    try {
      await api.delete(`/api/v1/erp/suppliers/${id}`);
      fetchSuppliers();
    } catch (e: any) {
      alert(e.response?.data?.detail || '删除失败');
    }
  };

  return (
    <div className="p-8 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Users className="text-orange-400" />
            供应商管理
          </h2>
          <p className="text-gray-400 text-sm mt-1">管理供应商信息</p>
        </div>
        <button onClick={openCreate} className="bg-orange-500/20 text-orange-400 border border-orange-500/50 hover:bg-orange-500/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Plus className="w-4 h-4" /> 新增供应商
        </button>
      </div>

      <div className="mb-6 flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input type="text" value={keyword} onChange={e => setKeyword(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetchSuppliers()} placeholder="搜索供应商编码或名称..." className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-orange-500/50" />
        </div>
        <button onClick={fetchSuppliers} className="bg-white/5 border border-white/10 hover:bg-white/10 px-4 py-2 rounded-lg text-sm text-gray-300 transition-colors">搜索</button>
      </div>

      <div className="glass-panel flex-1 rounded-2xl overflow-y-auto border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
              <th className="p-4 font-medium">编码</th>
              <th className="p-4 font-medium">名称</th>
              <th className="p-4 font-medium">联系人</th>
              <th className="p-4 font-medium">电话</th>
              <th className="p-4 font-medium">邮箱</th>
              <th className="p-4 font-medium">状态</th>
              <th className="p-4 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map(s => (
              <tr key={s.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                <td className="p-4 font-mono text-orange-400">{s.code}</td>
                <td className="p-4 text-gray-200">{s.name}</td>
                <td className="p-4 text-gray-300">{s.contact_person || '-'}</td>
                <td className="p-4 text-gray-300">{s.phone || '-'}</td>
                <td className="p-4 text-gray-400">{s.email || '-'}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-1 rounded-md border ${s.status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' : 'bg-red-500/20 text-red-400 border-red-500/50'}`}>
                    {s.status === 'ACTIVE' ? '正常' : '黑名单'}
                  </span>
                </td>
                <td className="p-4 flex gap-2">
                  <button onClick={() => openEdit(s)} className="text-blue-400 hover:text-blue-300 transition-colors">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDelete(s.id)} className="text-red-400 hover:text-red-300 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {suppliers.length === 0 && (
              <tr><td colSpan={7} className="p-8 text-center text-gray-500">暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">{editingId ? '编辑供应商' : '新增供应商'}</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">供应商编码</label>
                  <input value={formData.code} onChange={e => setFormData({...formData, code: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-orange-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">名称</label>
                  <input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-orange-500/50" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">联系人</label>
                  <input value={formData.contact_person} onChange={e => setFormData({...formData, contact_person: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-orange-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">电话</label>
                  <input value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-orange-500/50" />
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">邮箱</label>
                <input value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-orange-500/50" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">取消</button>
              <button onClick={handleSave} className="bg-orange-500/20 text-orange-400 border border-orange-500/50 hover:bg-orange-500/30 px-4 py-2 rounded-lg transition-colors">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
