import React, { useState, useEffect } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  TrendingUp, 
  Terminal, 
  Database, 
  Menu, 
  ChevronLeft, 
  ChevronRight,
  Activity,
  Settings,
  User
} from 'lucide-react';
import { checkDatabaseHealth } from '../services/api';

export default function Layout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [dbStatus, setDbStatus] = useState({ status: 'loading', database: 'unknown' });
  const location = useLocation();

  useEffect(() => {
    // Run initial check and set interval for database connection polling
    const fetchHealth = async () => {
      const health = await checkDatabaseHealth();
      setDbStatus(health);
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000); // Poll every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Inventory Ledger', path: '/ledger', icon: Package },
    { name: 'Forecast Models', path: '/forecasts', icon: TrendingUp },
    { name: 'System Logs', path: '/logs', icon: Terminal },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <div className="flex h-screen bg-brand-dark text-slate-100 overflow-hidden relative">
      {/* Backdrop for Mobile Drawer */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden transition-opacity duration-300"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Mobile Sidebar Navigation Drawer */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#161b26]/95 backdrop-blur-2xl border-r border-brand-border flex flex-col transition-transform duration-300 md:hidden ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-brand-border">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-accent flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
              O
            </div>
            <span className="font-semibold text-lg tracking-wider bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              OpsMind AI
            </span>
          </div>
          <button 
            onClick={() => setIsMobileOpen(false)}
            className="p-1.5 rounded-md hover:bg-brand-border text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ChevronLeft size={20} />
          </button>
        </div>

        {/* Navigation Indices */}
        <nav className="flex-1 py-4 space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setIsMobileOpen(false)}
                className={`flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-brand-accent text-white shadow-lg shadow-blue-500/10' 
                    : 'text-slate-400 hover:bg-brand-border hover:text-slate-100'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-white' : 'text-slate-400'} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Operational Version */}
        <div className="p-4 border-t border-brand-border text-xs text-slate-500 text-center">
          <span>Version 1.0.0 (Phase 4)</span>
        </div>
      </aside>

      {/* Desktop Sidebar Navigation */}
      <aside 
        className={`bg-brand-card/30 backdrop-blur-xl border-r border-brand-border flex-col transition-all duration-300 hidden md:flex ${
          isCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-brand-border">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-brand-accent flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
                O
              </div>
              <span className="font-semibold text-lg tracking-wider bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                OpsMind AI
              </span>
            </div>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 mx-auto rounded-lg bg-brand-accent flex items-center justify-center font-bold text-white">
              O
            </div>
          )}
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded-md hover:bg-brand-border text-slate-400 hover:text-slate-200 transition-colors"
          >
            {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation Indices */}
        <nav className="flex-1 py-4 space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-brand-accent text-white shadow-lg shadow-blue-500/10' 
                    : 'text-slate-400 hover:bg-brand-border hover:text-slate-100'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-white' : 'text-slate-400'} />
                {!isCollapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Operational Version */}
        <div className="p-4 border-t border-brand-border text-xs text-slate-500 text-center">
          {!isCollapsed && <span>Version 1.0.0 (Phase 4)</span>}
          {isCollapsed && <span>v1.0</span>}
        </div>
      </aside>

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Status Utility Header */}
        <header className="bg-brand-card/30 backdrop-blur-lg p-5 rounded-2xl border border-brand-border flex items-center gap-4 hover:scale-105 transform transition-transform duration-200 shadow-lg justify-between px-6 z-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsMobileOpen(true)}
              className="p-1.5 rounded-lg bg-brand-card border border-brand-border text-slate-400 hover:text-white md:hidden transition-colors"
              aria-label="Open navigation menu"
            >
              <Menu size={18} />
            </button>
            <h1 className="font-semibold text-lg text-slate-200">
              {navItems.find(item => item.path === location.pathname)?.name || 'Application'}
            </h1>
          </div>

          {/* live Database Handshake Connection Header */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-brand-border/40 px-3 py-1.5 rounded-full border border-brand-border">
              <Database size={14} className={dbStatus.database === 'connected' ? 'text-brand-success' : 'text-brand-danger'} />
              <span className="text-xs font-medium text-slate-300">
                Supabase: 
              </span>
              <span className={`text-xs font-semibold uppercase ${
                dbStatus.database === 'connected' ? 'text-brand-success' : 'text-brand-danger'
              }`}>
                {dbStatus.database === 'connected' ? 'Connected' : 'Offline'}
              </span>
            </div>
            
            <div className="w-2 h-2 rounded-full bg-brand-success animate-pulse" title="System online" />
          </div>
        </header>

        {/* View Switch Container */}
        <main className="flex-1 overflow-y-auto p-6 bg-brand-dark">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
