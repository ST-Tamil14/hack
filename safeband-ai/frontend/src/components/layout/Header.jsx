import { Menu, Bell, Search, RefreshCw, AlertTriangle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { timeAgo } from '../../utils/formatDate';

export default function Header({ onMenuClick, title, subtitle }) {
  const { state } = useApp();

  const statusConfig = {
    online:   { color: 'bg-green-500', label: 'Online',      ring: 'ring-green-200' },
    offline:  { color: 'bg-red-500',   label: 'Offline',     ring: 'ring-red-200' },
    checking: { color: 'bg-yellow-400',label: 'Connecting…', ring: 'ring-yellow-200' },
  };
  const status = statusConfig[state.systemStatus] || statusConfig.checking;

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-slate-200 px-4 lg:px-6 py-3">
      <div className="flex items-center gap-3">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Page title */}
        <div className="flex-1 min-w-0">
          <h1 className="text-lg font-bold text-slate-800 truncate leading-tight">{title}</h1>
          {subtitle && <p className="text-xs text-slate-500 truncate leading-tight">{subtitle}</p>}
        </div>

        {/* Right section */}
        <div className="flex items-center gap-2 ml-auto">
          {/* System status indicator */}
          <div className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ring-2 ${status.ring} border-transparent`}>
            <span className={`w-2 h-2 rounded-full ${status.color} dot-blink flex-shrink-0`} />
            <span className="text-slate-600">Backend {status.label}</span>
          </div>

          {/* Last updated */}
          {state.lastUpdated && (
            <div className="hidden md:flex items-center gap-1 text-xs text-slate-400">
              <RefreshCw className="w-3 h-3" />
              <span>{timeAgo(state.lastUpdated)}</span>
            </div>
          )}

          {/* Active alerts bell */}
          <div className="relative">
            <button className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors">
              <Bell className="w-4 h-4" />
            </button>
            {state.activeAlertCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 flex items-center justify-center bg-red-500 text-white text-[10px] font-bold rounded-full">
                {state.activeAlertCount > 9 ? '9+' : state.activeAlertCount}
              </span>
            )}
          </div>

          {/* User badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-brand-50 rounded-lg border border-brand-100">
            <div className="w-6 h-6 rounded-full bg-brand-600 flex items-center justify-center">
              <span className="text-white text-[10px] font-bold">SB</span>
            </div>
            <div className="text-xs">
              <p className="font-semibold text-slate-700 leading-tight">Caregiver</p>
              <p className="text-slate-400 leading-tight">{state.userId}</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
