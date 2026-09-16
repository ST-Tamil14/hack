import { Bell, RefreshCw } from 'lucide-react';
import NotificationTable from '../components/notifications/NotificationTable';
import ErrorState from '../components/ui/ErrorState';
import { useNotifications } from '../hooks/useNotifications';

export default function NotificationHistory() {
  const { notifications, loading, error, actionLoading, acknowledge, resolve, refetch } = useNotifications(10000);

  return (
    <div className="space-y-4 fade-in">
      {/* Header stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Total',        count: notifications.length,                                               color: 'text-slate-700' },
          { label: 'Active',       count: notifications.filter(n => n.status !== 'resolved' && n.status !== 'acknowledged').length, color: 'text-red-600' },
          { label: 'Acknowledged', count: notifications.filter(n => n.status === 'acknowledged').length,      color: 'text-cyan-600' },
          { label: 'Resolved',     count: notifications.filter(n => n.status === 'resolved').length,          color: 'text-green-600' },
        ].map(({ label, count, color }) => (
          <div key={label} className="card p-3">
            <p className="text-xs text-slate-400">{label}</p>
            <p className={`text-xl font-bold ${color}`}>{count}</p>
          </div>
        ))}
      </div>

      {/* Table card */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-brand-600" />
            <p className="section-title">Notification History</p>
          </div>
          <button onClick={refetch} className="btn-secondary text-xs py-1.5">
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={refetch} />
        ) : (
          <NotificationTable
            notifications={notifications}
            loading={loading}
            onAcknowledge={acknowledge}
            onResolve={resolve}
            actionLoading={actionLoading}
          />
        )}
      </div>

      <p className="text-xs text-slate-400 text-center">
        Showing emergency notifications for user: <span className="font-medium">see sidebar for active user</span>.
        Data auto-refreshes every 10 seconds.
      </p>
    </div>
  );
}
