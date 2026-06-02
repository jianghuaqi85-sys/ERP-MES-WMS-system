import React, { useEffect, useState } from 'react';
import { Search, Activity, Package, ClipboardList, ShoppingCart, Users, Database, TrendingUp, Clock } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell } from 'recharts';
import api from '../utils/axios';
import { TraceabilityGraph } from '../components/TraceabilityGraph';
import { InfoPanel } from '../components/InfoPanel';
import { toast } from 'sonner';

interface DashboardStats {
  total_products: number;
  total_materials: number;
  total_work_orders: number;
  pending_work_orders: number;
  in_progress_work_orders: number;
  completed_work_orders: number;
  total_sales_orders: number;
  pending_sales_orders: number;
  total_suppliers: number;
}

const MOCK_NODES = [
  { id: 'erp-product-1', position: { x: 400, y: 50 }, data: { label: 'Product: iPhone 16 Pro', type: 'ERP - Finished Good' }, style: { background: '#27272a', border: '1px solid #3f3f46', color: '#e4e4e7', borderRadius: '4px', padding: '10px' } },
  { id: 'mes-wo-1', position: { x: 400, y: 200 }, data: { label: 'WO: WO-A9F8E7D6', type: 'MES - Work Order' }, style: { background: '#27272a', border: '1px solid #3f3f46', color: '#e4e4e7', borderRadius: '4px', padding: '10px' } },
  { id: 'wms-mat-1', position: { x: 200, y: 350 }, data: { label: 'Mat: Screen Panel', type: 'WMS - Raw Material' }, style: { background: '#27272a', border: '1px solid #3f3f46', color: '#e4e4e7', borderRadius: '4px', padding: '10px' } },
];
const MOCK_EDGES = [
  { id: 'e1-2', source: 'mes-wo-1', target: 'erp-product-1', animated: false, style: { stroke: '#52525b' } },
  { id: 'e2-3', source: 'wms-mat-1', target: 'mes-wo-1', animated: false, style: { stroke: '#52525b' } },
];

const mockProductionData = [
  { name: 'Mon', target: 400, actual: 240 },
  { name: 'Tue', target: 300, actual: 139 },
  { name: 'Wed', target: 200, actual: 980 },
  { name: 'Thu', target: 278, actual: 390 },
  { name: 'Fri', target: 189, actual: 480 },
  { name: 'Sat', target: 239, actual: 380 },
  { name: 'Sun', target: 349, actual: 430 },
];

const mockTimeline = [
  { time: '10:24 AM', title: 'Work Order WO-2023001 Completed', desc: '100 units of iPhone 16 Pro moved to WMS', type: 'success' },
  { time: '09:12 AM', title: 'Low Inventory Alert', desc: 'Screen Panels are running low in Zone A', type: 'warning' },
  { time: '08:00 AM', title: 'New Sales Order Created', desc: 'SO-10045 pending confirmation', type: 'info' },
  { time: 'Yesterday', title: 'System Backup', desc: 'Automated database backup completed', type: 'neutral' },
];

export const Dashboard: React.FC = () => {
  const [selectedNodeData, setSelectedNodeData] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [nodes, setNodes] = useState<any[]>(MOCK_NODES);
  const [edges, setEdges] = useState<any[]>(MOCK_EDGES);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [showGraph, setShowGraph] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/api/v1/system/dashboard/stats');
        setStats(res.data);
      } catch (e) {
        toast.error('获取统计数据失败');
      }
    };
    fetchStats();

    const ws = new WebSocket('ws://localhost:8001/api/v1/system/dashboard/ws');
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStats(data);
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    };

    ws.onerror = () => {
      console.error("WebSocket connection error");
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleSearch = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchTerm) {
      const toastId = toast.loading('正在追溯全链路数据...');
      try {
        const res = await api.get(`/api/v1/traceability/graph/${searchTerm}`);
        const newNodes = res.data.nodes.map((n: any, index: number) => ({
          ...n,
          position: { x: 400 + (index % 2 === 0 ? -150 : 150), y: 50 + index * 100 },
          style: { background: '#27272a', border: '1px solid #3f3f46', color: '#e4e4e7', borderRadius: '4px', padding: '10px' }
        }));
        setNodes(newNodes);
        setEdges(res.data.edges.map((edge: any) => ({ ...edge, animated: false, style: { stroke: '#52525b' } })));
        setShowGraph(true);
        toast.success('溯源成功', { id: toastId });
      } catch (err) {
        toast.error('未找到该条码的溯源数据', { id: toastId });
      }
    }
  };

  const statCards = stats ? [
    { label: '产品总数', value: stats.total_products, icon: <Package className="w-4 h-4" /> },
    { label: '物料总数', value: stats.total_materials, icon: <Database className="w-4 h-4" /> },
    { label: '工单总数', value: stats.total_work_orders, icon: <ClipboardList className="w-4 h-4" /> },
    { label: '进行中工单', value: stats.in_progress_work_orders, icon: <TrendingUp className="w-4 h-4" /> },
    { label: '销售订单', value: stats.total_sales_orders, icon: <ShoppingCart className="w-4 h-4" /> },
    { label: '供应商', value: stats.total_suppliers, icon: <Users className="w-4 h-4" /> },
  ] : [];

  const pieData = stats ? [
    { name: '进行中', value: stats.in_progress_work_orders || 1, color: '#3b82f6' },
    { name: '已完成', value: stats.completed_work_orders || 2, color: '#10b981' },
    { name: '未开始', value: stats.pending_work_orders || 1, color: '#71717a' },
  ] : [];

  return (
    <div className="h-full w-full flex flex-col relative bg-[#09090b]">
      {!showGraph ? (
        <div className="flex-1 overflow-auto p-6">
          <div className="mb-6 flex justify-between items-end border-b border-zinc-800 pb-4">
            <div>
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                数据仪表盘
              </h2>
              <p className="text-zinc-500 text-xs mt-1">系统核心运行指标监控</p>
            </div>
            <div className="text-right">
              <div className="text-xs text-zinc-500 font-mono">
                {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>

          {/* 统计卡片 */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            {statCards.map((card) => (
              <div
                key={card.label}
                className="glass-panel p-4 flex flex-col"
              >
                <div className="text-zinc-400 mb-2">{card.icon}</div>
                <div className="text-2xl font-semibold text-zinc-100 mb-1">{card.value}</div>
                <div className="text-xs text-zinc-500">{card.label}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            {/* 图表区 */}
            <div className="lg:col-span-2 glass-panel p-5">
              <h3 className="text-sm font-semibold mb-4 text-zinc-200">
                产能趋势 (近7日)
              </h3>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockProductionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                    <XAxis dataKey="name" stroke="#71717a" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#71717a" fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '4px', fontSize: '12px' }}
                      itemStyle={{ color: '#e4e4e7' }}
                    />
                    <Area type="monotone" dataKey="target" stroke="#52525b" fill="#27272a" strokeWidth={2} name="计划产能" />
                    <Area type="monotone" dataKey="actual" stroke="#3b82f6" fill="#1e3a8a" fillOpacity={0.2} strokeWidth={2} name="实际产能" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 工单分布 */}
            <div className="glass-panel p-5 flex flex-col">
               <h3 className="text-sm font-semibold mb-4 text-zinc-200">
                工单状态分布
              </h3>
              <div className="flex-1 relative min-h-[180px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={70}
                      paddingAngle={2}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '4px', fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                   <div className="text-xl font-bold text-zinc-200">{stats?.total_work_orders || 0}</div>
                   <div className="text-[10px] text-zinc-500">总计</div>
                </div>
              </div>
              <div className="mt-4 space-y-1.5">
                 {pieData.map(item => (
                   <div key={item.name} className="flex items-center justify-between text-xs">
                     <div className="flex items-center gap-2">
                       <span className="w-2 h-2 rounded-sm" style={{ backgroundColor: item.color }}></span>
                       <span className="text-zinc-400">{item.name}</span>
                     </div>
                     <span className="text-zinc-300 font-medium">{item.value}</span>
                   </div>
                 ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* 溯源搜索 */}
            <div className="glass-panel p-6">
              <h3 className="text-sm font-semibold mb-2 text-zinc-200">
                全链路溯源查询
              </h3>
              <p className="text-zinc-500 text-xs mb-4">输入条码查询原料、工序及成品完整链路</p>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <input
                  type="text"
                  placeholder="扫描或输入条码 (Enter)"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  onKeyDown={handleSearch}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded py-2 pl-9 pr-3 text-sm text-zinc-200 focus:outline-none focus:border-zinc-500 transition-colors placeholder:text-zinc-600"
                />
              </div>
            </div>

            {/* 实时动态时间轴 */}
            <div className="glass-panel p-5">
               <h3 className="text-sm font-semibold mb-4 text-zinc-200 flex items-center gap-2">
                <Clock className="w-4 h-4 text-zinc-400" />
                系统操作日志
              </h3>
              <div className="space-y-4">
                {mockTimeline.map((item, idx) => (
                  <div key={idx} className="flex gap-3 relative">
                    {idx !== mockTimeline.length - 1 && (
                      <div className="absolute left-[5px] top-4 bottom-[-16px] w-px bg-zinc-800"></div>
                    )}
                    <div className="mt-1">
                      <div className={`w-3 h-3 rounded-sm 
                        ${item.type === 'success' ? 'bg-emerald-500/20 border border-emerald-500/50' : 
                          item.type === 'warning' ? 'bg-amber-500/20 border border-amber-500/50' : 
                          item.type === 'info' ? 'bg-blue-500/20 border border-blue-500/50' : 'bg-zinc-700 border border-zinc-600'}`}>
                      </div>
                    </div>
                    <div className="flex-1 pb-1">
                      <div className="flex justify-between items-start mb-0.5">
                        <div className="text-xs font-medium text-zinc-300">{item.title}</div>
                        <div className="text-[10px] text-zinc-500 font-mono">{item.time}</div>
                      </div>
                      <div className="text-xs text-zinc-500">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-[#18181b]">
            <div className="flex items-center gap-4">
              <button onClick={() => setShowGraph(false)} className="text-xs text-zinc-400 hover:text-zinc-200 transition-colors">
                ← 返回仪表盘
              </button>
              <div className="h-4 w-px bg-zinc-800"></div>
              <span className="text-sm font-medium text-zinc-300">追溯图谱</span>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
              <input
                type="text"
                placeholder="重新搜索..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                onKeyDown={handleSearch}
                className="w-full bg-zinc-950 border border-zinc-800 rounded py-1.5 pl-8 pr-3 text-xs text-zinc-200 focus:outline-none focus:border-zinc-600 transition-colors"
              />
            </div>
          </div>
          <div className="flex-1 relative">
            <TraceabilityGraph
              onNodeClick={(e, node) => setSelectedNodeData(node.data)}
              initialNodes={nodes}
              initialEdges={edges}
            />
            <InfoPanel data={selectedNodeData} onClose={() => setSelectedNodeData(null)} />
          </div>
        </div>
      )}
    </div>
  );
};
