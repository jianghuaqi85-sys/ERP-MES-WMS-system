import React, { useEffect, useState } from 'react';
import { Package, Plus, Edit, Trash2, Search } from 'lucide-react';
import api from '../utils/axios';

interface Product {
  id: number;
  product_code: string;
  name: string;
  price: number;
  unit: string;
  description: string;
}

export const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState(new URLSearchParams(window.location.search).get('keyword') || '');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ product_code: '', name: '', price: 0, unit: 'pcs', description: '' });

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/erp/products', { params: { keyword } });
      setProducts(res.data.items);
    } catch (e) {
      console.error('获取产品列表失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleSearch = () => fetchProducts();

  const handleCreate = async () => {
    try {
      await api.post('/api/v1/erp/products', formData);
      setShowForm(false);
      setFormData({ product_code: '', name: '', price: 0, unit: 'pcs', description: '' });
      fetchProducts();
    } catch (e: any) {
      alert(e.response?.data?.detail || '创建失败');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此产品吗？')) return;
    try {
      await api.delete(`/api/v1/erp/products/${id}`);
      fetchProducts();
    } catch (e: any) {
      alert(e.response?.data?.detail || '删除失败');
    }
  };

  return (
    <div className="p-8 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Package className="text-blue-400" />
            产品管理
          </h2>
          <p className="text-gray-400 text-sm mt-1">管理成品基础数据</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-500/20 text-blue-400 border border-blue-500/50 hover:bg-blue-500/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus className="w-4 h-4" /> 新增产品
        </button>
      </div>

      {/* 搜索栏 */}
      <div className="mb-6 flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="搜索产品编码或名称..."
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500/50"
          />
        </div>
        <button onClick={handleSearch} className="bg-white/5 border border-white/10 hover:bg-white/10 px-4 py-2 rounded-lg text-sm text-gray-300 transition-colors">
          搜索
        </button>
      </div>

      {/* 表格 */}
      <div className="glass-panel flex-1 rounded-2xl overflow-y-auto border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 border-b border-white/10 text-gray-300 text-sm">
              <th className="p-4 font-medium">产品编码</th>
              <th className="p-4 font-medium">产品名称</th>
              <th className="p-4 font-medium">单价</th>
              <th className="p-4 font-medium">单位</th>
              <th className="p-4 font-medium">描述</th>
              <th className="p-4 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.id} className="border-b border-white/5 hover:bg-white/5 transition-colors text-sm">
                <td className="p-4 font-mono text-blue-400">{p.product_code}</td>
                <td className="p-4 text-gray-200">{p.name}</td>
                <td className="p-4 text-emerald-400">¥{p.price}</td>
                <td className="p-4 text-gray-400">{p.unit}</td>
                <td className="p-4 text-gray-500 max-w-xs truncate">{p.description || '-'}</td>
                <td className="p-4">
                  <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-300 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-gray-500">暂无数据</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* 新增表单弹窗 */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">新增产品</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">产品编码</label>
                <input value={formData.product_code} onChange={e => setFormData({...formData, product_code: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">产品名称</label>
                <input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">单价</label>
                  <input type="number" value={formData.price} onChange={e => setFormData({...formData, price: Number(e.target.value)})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">单位</label>
                  <input value={formData.unit} onChange={e => setFormData({...formData, unit: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50" />
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">描述</label>
                <textarea value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500/50 h-20 resize-none" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">取消</button>
              <button onClick={handleCreate} className="bg-blue-500/20 text-blue-400 border border-blue-500/50 hover:bg-blue-500/30 px-4 py-2 rounded-lg transition-colors">创建</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
