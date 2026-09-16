import { useState } from 'react';
import { User, Cpu, Database, Bell, CheckCircle, AlertTriangle, Activity, RefreshCw } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotifications } from '../hooks/useNotifications';
import { useSensorPolling } from '../hooks/useSensorPolling';
import { timeAgo } from '../utils/formatDate';

const MOCK_USERS = [
  { id: 'test-user-001', name: 'Test User 001', device: 'SafeBand-SIM-001' },
  { id: 'test-user-002', name: 'Test User 002', device: 'SafeBand-SIM-002' },
  { id: 'user-alice',    name: 'Alice Johnson', device: 'SafeBand-WB-101' },
  { id: 'user-bob',      name: 'Bob Williams',  device: 'SafeBand-WB-102' },
];

export default function Users() {
  const { state, dispatch } = useApp();
  const { notifications } = useNotifications();
  const { data, loading, readingCount, lastUpdated } = useSensorPolling(6000);

  const handleSelectUser = (id) => {
    dispatch({ type: 'SET_USER_ID', payload: id });
  };

  const totalFalls = notifications.filter((n) => n.notification_type === 'emergency_alert').length;
  const confirmedFalls = notifications.filter((n) => n.status !== 'simulated').length;
  const resolved = notifications.filter((n) => n.status === 'resolved').length;

  return (
    <div className="space-y-5 fade-in">
      {/* User selection */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <User className="w-4 h-4 text-brand-600" />
          <p className="section-title">Select Monitored User</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {MOCK_USERS.map((u) => {
            const isActive = state.userId === u.id;
            return (
              <button
                key={u.id}
                onClick={() => handleSelectUser(u.id)}
                className={`flex items-center gap-3 p-3 rounded-xl border text-left transition-all
                  ${isActive
                    ? 'border-brand-300 bg-brand-50 ring-2 ring-brand-200'
                    : 'border-slate-200 bg-white hover:bg-slate-50 hover:border-slate-300'}`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
                  ${isActive ? 'bg-brand-600' : 'bg-slate-200'}`}>
                  <User className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-semibold truncate ${isActive ? 'text-brand-700' : 'text-slate-700'}`}>
                    {u.name}
                  </p>
                  <p className="text-xs text-slate-400 truncate">{u.id}</p>
                  <p className="text-xs text-slate-400 truncate">{u.device}</p>
                </div>
                {isActive && <CheckCircle className="w-4 h-4 text-brand-600 flex-shrink-0" />}
              </button>
            );
          })}
        </div>
        <p className="text-xs text-slate-400 mt-3">
          * User list is mock-populated for prototype purposes. A real user-list endpoint is not yet available on the backend.
        </p>
      </div>

      {/* Active user stats */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <Cpu className="w-4 h-4 text-brand-600" />
          <p className="section-title">Active User — {state.userId}</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          {[
            { label: 'Device Status',          value: loading ? 'Connecting…' : 'Simulator', icon: Cpu,           color: 'text-brand-600' },
            { label: 'Total Readings',          value: readingCount,                          icon: Activity,      color: 'text-slate-700' },
            { label: 'Total Alerts',            value: notifications.length,                  icon: Bell,          color: 'text-blue-600' },
            { label: 'Resolved Alerts',         value: resolved,                              icon: CheckCircle,   color: 'text-green-600' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <div className="flex items-center gap-1 mb-1">
                <Icon className={`w-3.5 h-3.5 ${color}`} />
                <p className="text-slate-400">{label}</p>
              </div>
              <p className={`font-bold text-lg ${color}`}>{String(value)}</p>
            </div>
          ))}
        </div>
        {lastUpdated && (
          <p className="text-xs text-slate-400 mt-3">Last data: {timeAgo(lastUpdated)}</p>
        )}
      </div>

      {/* Recent alerts for this user */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle className="w-4 h-4 text-orange-500" />
          <p className="section-title">Recent Alerts for {state.userId}</p>
        </div>
        {notifications.length === 0 ? (
          <p className="text-sm text-slate-400">No alerts found for this user.</p>
        ) : (
          <div className="space-y-2">
            {notifications.slice(0, 5).map((n) => (
              <div key={n.id} className="flex items-center justify-between text-xs px-3 py-2 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-slate-600 truncate flex-1">{n.message}</span>
                <span className="font-semibold text-slate-500 ml-2 capitalize">{n.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
