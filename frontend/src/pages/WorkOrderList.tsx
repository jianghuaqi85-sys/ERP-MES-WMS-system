import React, { useEffect, useState } from 'react';
import { ClipboardList, Play, Search, CheckCircle, Filter, Download, Plus, X } from 'lucide-react';
import { VirtuosoGrid } from 'react-virtuoso';
import { toast } from 'sonner';
import api from '../utils/axios';

interface WorkOrder {
  id: number;
  work_order_number: string;
  product_id: number;
  planned_quantity: number;
  actual_quantity: number;
  qualified_quantity: number;
  defective_quantity: number;
  status: string;
}

interface ConsumedMaterial {
  material_id: number;
  quantity: number;
  inventory_location_code: string;
  material_barcode: string;
}

const statusMap: Record<string, { label: string; color: string; border: string }> = {
  PLANNED: { label: '已计划', color: 'bg-zinc-800 text-zinc-400', border: 'border-zinc-700' },
  NOT_STARTED: { label: '未开始', color: 'bg-amber-900/30 text-amber-400', border: 'border-amber-800/50' },
  IN_PROGRESS: { label: '进行中', color: 'bg-blue-900/30 text-blue-400', border: 'border-blue-800/50' },
  COMPLETED: { label: '已完成', color: 'bg-emerald-900/30 text-emerald-400', border: 'border-emerald-800/50' },
  CLOSED: { label: '已关闭', color: 'bg-purple-900/30 text-purple-400', border: 'border-purple-800/50' },
};

export const WorkOrderList: React.FC = () => {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReport, setShowReport] = useState(false);
  const [selectedWO, setSelectedWO] = useState<WorkOrder | null>(null);
  const [searchTerm, setSearchTerm] = useState(new URLSearchParams(window.location.search).get('search') || '');
  
  const [reportForm, setReportForm] = useState({
    produced_quantity: 1,
    qualified_quantity: 0,
    defective_quantity: 0,
    product_barcode: '',
    consumed_materials: [{ material_id: 0, quantity: 1, inventory_location_code: '', material_barcode: '' }] as ConsumedMaterial[],
  });

  const fetchWorkOrders = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/mes/work-orders');
      setWorkOrders(res.data.items);
    } catch (e) {
      toast.error('获取工单列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchWorkOrders(); }, []);

  const openReport = (wo: WorkOrder) => {
    setSelectedWO(wo);
    setReportForm({
      produced_quantity: 1,
      qualified_quantity: 0,
      defective_quantity: 0,
      product_barcode: '',
      consumed_materials: [{ material_id: 0, quantity: 1, inventory_location_code: '', material_barcode: '' }],
    });
    setShowReport(true);
  };

  const handleReport = async () => {
    if (!selectedWO) return;
    const toastId = toast.loading('正在提交报工数据...');
    try {
      await api.post(`/api/v1/mes/work-orders/${selectedWO.id}/report`, reportForm);
      toast.success('报工成功！', { id: toastId });
      setShowReport(false);
      fetchWorkOrders();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || '报工失败', { id: toastId });
    }
  };

  const addMaterial = () => {
    setReportForm({
      ...reportForm,
      consumed_materials: [...reportForm.consumed_materials, { material_id: 0, quantity: 1, inventory_location_code: '', material_barcode: '' }],
    });
  };

  const removeMaterial = (index: number) => {
    setReportForm({
      ...reportForm,
      consumed_materials: reportForm.consumed_materials.filter((_, i) => i !== index),
    });
  };

  const updateMaterial = (index: number, field: keyof ConsumedMaterial, value: any) => {
    const materials = [...reportForm.consumed_materials];
    materials[index] = { ...materials[index], [field]: value };
    setReportForm({ ...reportForm, consumed_materials: materials });
  };

  const filteredOrders = workOrders.filter(wo => wo.work_order_number.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="p-6 h-full flex flex-col bg-[#09090b]">
      {/* 页面头部 */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-end mb-6 gap-4 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            生产工单
          </h2>
          <p className="text-zinc-500 text-xs mt-1">管理生产计划执行、报工与质量追踪</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
            <input 
              type="text" 
              placeholder="搜索工单号..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-56 bg-zinc-950 border border-zinc-800 rounded py-1.5 pl-8 pr-3 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors"
            />
          </div>
          <button className="glass-panel px-3 py-1.5 rounded text-xs text-zinc-300 hover:text-white flex items-center gap-1.5 hover:bg-zinc-800 transition-colors">
            <Filter className="w-3.5 h-3.5" /> 筛选
          </button>
          <button className="glass-panel px-3 py-1.5 rounded text-xs text-zinc-300 hover:text-white flex items-center gap-1.5 hover:bg-zinc-800 transition-colors">
            <Download className="w-3.5 h-3.5" /> 导出
          </button>
          <button className="bg-emerald-700 hover:bg-emerald-600 text-white px-3 py-1.5 rounded text-xs font-medium flex items-center gap-1.5 transition-colors">
            <Plus className="w-3.5 h-3.5" /> 新建工单
          </button>
        </div>
      </div>

      {/* 工单列表 */}
      <div style={{ height: "calc(100vh - 170px)" }}>
        {loading ? (
          <div className="flex items-center justify-center h-64 text-zinc-500 text-sm">加载中...</div>
        ) : filteredOrders.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 glass-panel border border-zinc-800">
            <div className="text-zinc-500 text-sm">未找到相关工单数据</div>
          </div>
        ) : (
          <VirtuosoGrid
            style={{ height: '100%' }}
            totalCount={filteredOrders.length}
            overscan={200}
            listClassName="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 auto-rows-max"
            itemContent={(index) => {
              const wo = filteredOrders[index];
              return (
              <div key={wo.id} className="glass-panel glass-panel-hover p-4 flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <span className="font-mono text-sm font-semibold text-zinc-200">{wo.work_order_number}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border ${statusMap[wo.status]?.color} ${statusMap[wo.status]?.border}`}>
                    {statusMap[wo.status]?.label || wo.status}
                  </span>
                </div>

                <div className="space-y-3 mb-4 flex-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-zinc-500">产品 ID:</span>
                    <span className="text-zinc-300 font-mono">PRD-{wo.product_id}</span>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-zinc-500">进度:</span>
                      <span className="text-zinc-300">{wo.actual_quantity} / {wo.planned_quantity}</span>
                    </div>
                    <div className="w-full bg-zinc-800 rounded-sm h-1">
                      <div
                        className="bg-emerald-500 h-full rounded-sm"
                        style={{ width: `${Math.min(100, (wo.actual_quantity / wo.planned_quantity) * 100)}%` }}
                      />
                    </div>
                  </div>

                  {wo.qualified_quantity > 0 && (
                    <div className="flex justify-between text-xs pt-2 border-t border-zinc-800">
                      <span className="text-zinc-500">良/不良:</span>
                      <span className="text-zinc-300">
                        <span className="text-emerald-400">{wo.qualified_quantity}</span>
                        <span className="text-zinc-600 mx-1">/</span>
                        <span className="text-red-400">{wo.defective_quantity}</span>
                      </span>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => openReport(wo)}
                  disabled={wo.status === 'COMPLETED' || wo.status === 'CLOSED'}
                  className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs py-1.5 rounded flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-zinc-700"
                >
                  {wo.status === 'COMPLETED' || wo.status === 'CLOSED' ? (
                    <><CheckCircle className="w-3.5 h-3.5" /> 已完成</>
                  ) : (
                    <><Play className="w-3.5 h-3.5" /> 生产报工</>
                  )}
                </button>
              </div>
              );
            }}
          />
        )}
      </div>

      {/* 报工弹窗 (精简扁平化版) */}
      {showReport && selectedWO && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="glass-panel border-zinc-700 rounded-md w-full max-w-xl z-10 flex flex-col max-h-[85vh] shadow-2xl">
            <div className="flex justify-between items-center p-4 border-b border-zinc-800 bg-[#18181b]">
              <div>
                <h3 className="text-sm font-bold text-zinc-100">生产报工</h3>
                <p className="text-zinc-500 text-[10px] mt-0.5 font-mono">{selectedWO.work_order_number}</p>
              </div>
              <button onClick={() => setShowReport(false)} className="text-zinc-500 hover:text-zinc-300 transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 overflow-y-auto bg-[#09090b] flex-1">
              <div className="space-y-4">
                {/* 产出数据 */}
                <div className="border border-zinc-800 p-3 rounded bg-[#18181b]">
                  <h4 className="text-xs font-semibold text-zinc-300 mb-3 border-l-2 border-emerald-500 pl-2">
                    产出数据
                  </h4>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-[10px] text-zinc-500 mb-1">产出总量</label>
                      <input type="number" value={reportForm.produced_quantity} onChange={e => setReportForm({...reportForm, produced_quantity: Number(e.target.value)})} className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors" />
                    </div>
                    <div>
                      <label className="block text-[10px] text-zinc-500 mb-1">合格数量</label>
                      <input type="number" value={reportForm.qualified_quantity} onChange={e => setReportForm({...reportForm, qualified_quantity: Number(e.target.value)})} className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-emerald-400 focus:outline-none focus:border-zinc-500 transition-colors" />
                    </div>
                    <div>
                      <label className="block text-[10px] text-zinc-500 mb-1">不良数量</label>
                      <input type="number" value={reportForm.defective_quantity} onChange={e => setReportForm({...reportForm, defective_quantity: Number(e.target.value)})} className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-red-400 focus:outline-none focus:border-zinc-500 transition-colors" />
                    </div>
                  </div>
                </div>

                {/* 追溯信息 */}
                <div className="border border-zinc-800 p-3 rounded bg-[#18181b]">
                  <h4 className="text-xs font-semibold text-zinc-300 mb-3 border-l-2 border-blue-500 pl-2">
                    追溯绑定
                  </h4>
                  <div>
                    <label className="block text-[10px] text-zinc-500 mb-1">生成/绑定的成品条码</label>
                    <input value={reportForm.product_barcode} onChange={e => setReportForm({...reportForm, product_barcode: e.target.value})} placeholder="扫描或输入条码" className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors font-mono" />
                  </div>
                </div>

                {/* 物料消耗 */}
                <div className="border border-zinc-800 p-3 rounded bg-[#18181b]">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-xs font-semibold text-zinc-300 border-l-2 border-amber-500 pl-2">
                      物料消耗
                    </h4>
                    <button onClick={addMaterial} className="text-amber-500 hover:text-amber-400 text-[10px] font-medium flex items-center gap-1 transition-colors">
                      <Plus className="w-3 h-3" /> 添加物料
                    </button>
                  </div>
                  
                  <div className="space-y-2">
                    {reportForm.consumed_materials.map((mat, idx) => (
                      <div key={idx} className="flex gap-2 items-start group">
                        <input type="number" placeholder="物料ID" value={mat.material_id || ''} onChange={e => updateMaterial(idx, 'material_id', Number(e.target.value))} className="w-1/4 bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors" />
                        <input type="number" placeholder="数量" value={mat.quantity || ''} onChange={e => updateMaterial(idx, 'quantity', Number(e.target.value))} className="w-1/4 bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors" />
                        <input placeholder="库位" value={mat.inventory_location_code} onChange={e => updateMaterial(idx, 'inventory_location_code', e.target.value)} className="w-1/4 bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors" />
                        <div className="w-1/4 relative">
                           <input placeholder="条码" value={mat.material_barcode} onChange={e => updateMaterial(idx, 'material_barcode', e.target.value)} className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors font-mono" />
                           {reportForm.consumed_materials.length > 1 && (
                            <button onClick={() => removeMaterial(idx)} className="absolute -right-6 top-1.5 opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-400 transition-opacity">
                              <X className="w-3.5 h-3.5" />
                            </button>
                           )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-zinc-800 bg-[#18181b] flex justify-end gap-2">
              <button onClick={() => setShowReport(false)} className="px-4 py-1.5 rounded text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors border border-transparent">取消</button>
              <button onClick={handleReport} className="bg-emerald-700 hover:bg-emerald-600 text-white px-4 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" /> 确认报工
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
