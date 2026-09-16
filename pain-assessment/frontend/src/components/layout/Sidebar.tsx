import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Video,
  FileText,
  Bell,
  Settings,
  Activity,
  HeartPulse,
} from 'lucide-react';

interface SidebarProps {
  activeSessionId?: string;
}

export const Sidebar: React.FC<SidebarProps> = () => {
  const navItems = [
    { to: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
    { to: '/patients', label: 'Patient Roster', icon: Users },
    { to: '/assessment/new', label: 'Live Assessment', icon: Video, badge: 'LIVE' },
    { to: '/reports', label: 'Assessment Reports', icon: FileText },
    { to: '/alerts', label: 'Clinical Alerts', icon: Bell },
    { to: '/settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 flex-shrink-0 hidden md:flex">
      <div className="space-y-6">
        {/* Navigation Section */}
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Clinical Navigation
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-50 text-cyan-700 font-semibold border border-cyan-200/80 shadow-2xs'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`
                  }
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="bg-rose-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md animate-pulse">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Multimodal Modalities Quick Guide */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-900">
            <HeartPulse className="w-4 h-4 text-cyan-600" />
            <span>Multimodal AI Engine</span>
          </div>
          <div className="text-[11px] text-slate-500 space-y-1">
            <div className="flex items-center justify-between">
              <span>• Facial Analysis</span>
              <span className="text-emerald-600 font-medium">Ready</span>
            </div>
            <div className="flex items-center justify-between">
              <span>• Physiological rPPG</span>
              <span className="text-emerald-600 font-medium">Ready</span>
            </div>
            <div className="flex items-center justify-between">
              <span>• Behavioral Tracking</span>
              <span className="text-emerald-600 font-medium">Ready</span>
            </div>
            <div className="flex items-center justify-between">
              <span>• Acoustic Vocal Noise</span>
              <span className="text-emerald-600 font-medium">Ready</span>
            </div>
          </div>
        </div>
      </div>

      {/* Safety Compliance Footer */}
      <div className="border-t border-slate-200 pt-3 text-[11px] text-slate-400 space-y-1">
        <div className="flex items-center space-x-1.5 font-medium text-slate-500">
          <Activity className="w-3.5 h-3.5 text-teal-600" />
          <span>SaMD Class II Assistive</span>
        </div>
        <p>Continuous AI validation active.</p>
      </div>
    </aside>
  );
};
