import React, { useState, useEffect, useRef } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Activity, Box, ClipboardList, Database, LogOut, Package,
  ShoppingCart, Truck, Users, FileText, Bell, Search
} from 'lucide-react';

export const Layout: React.FC = () => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const searchRef = useRef<HTMLDivElement>(null);

  const searchItems = [
    { name: '数据仪表盘 (Dashboard)', path: '/', category: '导航跳转' },
    { name: '商品管理 (Products)', path: '/erp/products', category: '导航跳转' },
    { name: 'BOM 管理 (BOM List)', path: '/erp/boms', category: '导航跳转' },
    { name: '销售订单 (Sales Orders)', path: '/erp/sales-orders', category: '导航跳转' },
    { name: '供应商管理 (Suppliers)', path: '/erp/suppliers', category: '导航跳转' },
    { name: '采购订单 (Purchase Orders)', path: '/erp/purchase-orders', category: '导航跳转' },
    { name: '生产工单 (Work Orders)', path: '/mes/work-orders', category: '导航跳转' },
    { name: '库存管理 (WMS Inventory)', path: '/wms/inventory', category: '导航跳转' },
  ];

  const filteredSearchItems = searchItems.filter(item => 
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const dynamicItems = [];
  if (searchQuery.trim()) {
    const q = searchQuery.toUpperCase();
    if (q.startsWith('WO-') || /^\d+$/.test(q)) {
      dynamicItems.push({
        name: `在生产工单中搜索 "${q}"`,
        path: `/mes/work-orders?search=${q}`,
        category: '快速搜索'
      });
    }
    if (q.startsWith('PRD-') || q.startsWith('PROD-')) {
      dynamicItems.push({
        name: `在商品管理中搜索 "${q}"`,
        path: `/erp/products?keyword=${q}`,
        category: '快速搜索'
      });
    }
    if (q.startsWith('SUP-')) {
      dynamicItems.push({
        name: `在供应商管理中搜索 "${q}"`,
        path: `/erp/suppliers?keyword=${q}`,
        category: '快速搜索'
      });
    }
    if (q.startsWith('SO-')) {
      dynamicItems.push({
        name: `在销售订单中搜索 "${q}"`,
        path: `/erp/sales-orders?keyword=${q}`,
        category: '快速搜索'
      });
    }
    if (q.startsWith('PO-')) {
      dynamicItems.push({
        name: `在采购订单中搜索 "${q}"`,
        path: `/erp/purchase-orders?keyword=${q}`,
        category: '快速搜索'
      });
    }
    if (q.startsWith('MAT-')) {
      dynamicItems.push({
        name: `在库存管理中搜索 "${q}"`,
        path: `/wms/inventory?keyword=${q}`,
        category: '快速搜索'
      });
    }
  }
  const allFiltered = [...filteredSearchItems, ...dynamicItems];

  const handleSearchNavigate = (path: string) => {
    navigate(path);
    setSearchQuery('');
    setSearchOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchOpen(prev => !prev);
        const input = document.getElementById('global-search-input');
        if (input) {
          input.focus();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const navSections = [
    {
      title: '总览',
      items: [
        { name: '数据仪表盘', path: '/', icon: <Activity className="w-4 h-4" /> },
      ],
    },
    {
      title: 'ERP 管理',
      items: [
        { name: '产品管理', path: '/erp/products', icon: <Package className="w-4 h-4" /> },
        { name: 'BOM 物料清单', path: '/erp/boms', icon: <FileText className="w-4 h-4" /> },
        { name: '销售订单', path: '/erp/sales-orders', icon: <ShoppingCart className="w-4 h-4" /> },
        { name: '供应商管理', path: '/erp/suppliers', icon: <Users className="w-4 h-4" /> },
        { name: '采购订单', path: '/erp/purchase-orders', icon: <Truck className="w-4 h-4" /> },
      ],
    },
    {
      title: 'MES 生产',
      items: [
        { name: '生产工单', path: '/mes/work-orders', icon: <ClipboardList className="w-4 h-4" /> },
      ],
    },
    {
      title: 'WMS 仓储',
      items: [
        { name: '库存管理', path: '/wms/inventory', icon: <Database className="w-4 h-4" /> },
      ],
    },
  ];

  return (
    <div className="h-screen w-screen flex bg-background text-zinc-300 overflow-hidden font-sans text-sm">
      {/* 侧边栏 */}
      <aside className="w-56 glass-panel border-r border-y-0 border-l-0 rounded-none flex flex-col z-20">
        <div className="h-12 flex items-center px-4 border-b border-zinc-800 shrink-0">
          <div className="w-6 h-6 rounded bg-zinc-800 flex items-center justify-center mr-2 border border-zinc-700">
            <Box className="w-3.5 h-3.5 text-zinc-300" />
          </div>
          <h1 className="text-sm font-semibold text-zinc-200 truncate tracking-tight">
            SYNCHRONY
          </h1>
        </div>

        <nav className="flex-1 py-4 px-2 space-y-4 overflow-y-auto">
          {navSections.map(section => (
            <div key={section.title}>
              <div className="px-2 pb-1.5 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
                {section.title}
              </div>
              <div className="space-y-0.5">
                {section.items.map(item => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center gap-2.5 px-2 py-1.5 rounded transition-colors duration-150 ${
                        isActive
                          ? 'bg-zinc-800 text-zinc-100'
                          : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                      }`}
                    >
                      <div className={isActive ? 'text-zinc-300' : 'text-zinc-500'}>
                        {item.icon}
                      </div>
                      <span className="font-medium">{item.name}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="p-2 border-t border-zinc-800">
          <button
            onClick={handleLogout}
            className="flex items-center gap-2.5 px-2 py-1.5 w-full rounded text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span className="font-medium text-sm">退出系统</span>
          </button>
        </div>
      </aside>

      {/* 右侧主体内容区域 */}
      <main className="flex-1 relative overflow-hidden flex flex-col bg-[#09090b]">
        {/* 顶部全局 Header */}
        <header className="h-12 border-b border-zinc-800 bg-[#18181b] flex items-center justify-between px-6 shrink-0 z-10">
          <div ref={searchRef} className="flex-1 max-w-md relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
            <input 
              id="global-search-input"
              type="text" 
              placeholder="搜索 (⌘+K)..." 
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setSearchOpen(true);
              }}
              onFocus={() => setSearchOpen(true)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && allFiltered.length > 0) {
                  handleSearchNavigate(allFiltered[0].path);
                }
                if (e.key === 'Escape') {
                  setSearchOpen(false);
                }
              }}
              className="w-full bg-zinc-950 border border-zinc-800 rounded py-1.5 pl-8 pr-3 text-xs text-zinc-300 focus:outline-none focus:border-zinc-600 transition-colors placeholder:text-zinc-600"
            />
            {searchOpen && (
              <div className="absolute left-0 right-0 top-full mt-1.5 bg-[#18181b] border border-zinc-800 rounded-md shadow-2xl max-h-80 overflow-y-auto z-50 p-1">
                {allFiltered.length === 0 ? (
                  <div className="p-3 text-xs text-zinc-500 text-center">未找到相关页面或操作</div>
                ) : (
                  <div>
                    {['导航跳转', '快速搜索'].map(cat => {
                      const catItems = allFiltered.filter(i => i.category === cat);
                      if (catItems.length === 0) return null;
                      return (
                        <div key={cat} className="mb-2 last:mb-0">
                          <div className="px-2 py-1 text-[9px] font-bold text-zinc-600 uppercase tracking-wider">{cat}</div>
                          <div className="space-y-0.5">
                            {catItems.map((item, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSearchNavigate(item.path)}
                                className="w-full text-left px-2.5 py-2 text-xs rounded hover:bg-zinc-800 text-zinc-300 hover:text-zinc-100 transition-colors flex items-center justify-between"
                              >
                                <span>{item.name}</span>
                                <span className="text-[10px] text-zinc-600 font-mono">Enter ↵</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            <button className="relative text-zinc-500 hover:text-zinc-300 transition-colors">
              <Bell className="w-4 h-4" />
            </button>
            <div className="w-6 h-6 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[10px] font-bold text-zinc-400 cursor-pointer hover:bg-zinc-700 transition-colors">
              AD
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
