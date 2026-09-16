import React from 'react';
import { Activity, Bell, User, ShieldAlert, Wifi, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';
import { AuthUser } from '../../types';

interface NavbarProps {
  user: AuthUser | null;
  unreadAlertsCount?: number;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, unreadAlertsCount = 1, onLogout }) => {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Clinical Title */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-500 flex items-center justify-center text-white shadow-sm">
            <Activity className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-900 text-lg tracking-tight">PainSense AI</span>
              <span className="bg-teal-50 text-teal-700 text-xs px-2 py-0.5 rounded-full font-medium border border-teal-200/60">
                Clinical v1.0
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Multimodal Pain & Physiological Monitoring Platform
            </p>
          </div>
        </div>

        {/* Center Disclaimers Badge */}
        <div className="hidden md:flex items-center space-x-2 bg-amber-50 border border-amber-200/70 text-amber-800 text-xs px-3 py-1.5 rounded-lg">
          <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>AI Assistive Estimates • Clinical Review Required</span>
        </div>

        {/* Right Action Icons */}
        <div className="flex items-center space-x-3">
          {/* Connection Status */}
          <div className="flex items-center space-x-1.5 text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200/60 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <Wifi className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Backend Online</span>
          </div>

          {/* Clinical Alerts Button */}
          <Link
            to="/alerts"
            className="relative p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            title="Clinical Alerts"
          >
            <Bell className="w-5 h-5" />
            {unreadAlertsCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-rose-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {unreadAlertsCount}
              </span>
            )}
          </Link>

          {/* Settings */}
          <Link
            to="/settings"
            className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </Link>

          {/* User Profile Dropdown / Badge */}
          <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
            <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-semibold text-xs">
              {user?.full_name?.substring(0, 2).toUpperCase() || 'DR'}
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-xs font-semibold text-slate-900 leading-none">
                {user?.full_name || 'Dr. Clinical User'}
              </div>
              <div className="text-[11px] text-slate-500 capitalize mt-0.5">{user?.role || 'Clinician'}</div>
            </div>
            <button
              onClick={onLogout}
              className="text-xs text-slate-500 hover:text-rose-600 ml-1 px-2 py-1 hover:bg-rose-50 rounded-md transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
