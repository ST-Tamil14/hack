import { AlertTriangle, CheckCircle, Clock, MapPin, User, Bell } from 'lucide-react';
import { getSeverityColors, getStatusColors } from '../../utils/riskHelpers';
import { formatDateTime, timeAgo } from '../../utils/formatDate';

export default function AlertCard({ notification, onAcknowledge, onResolve, actionLoading }) {
  const severity = (notification.severity || 'low').toLowerCase();
  const colors = getSeverityColors(severity);
  const statusCls = getStatusColors(notification.status);
  const isLoading = actionLoading === notification.id;
  const isResolved = notification.status === 'resolved';
  const isAcknowledged = notification.status === 'acknowledged';

  return (
    <div className={`card p-4 border-l-4 fade-in ${colors.border} ${colors.bg}`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${colors.text}`} />
          <p className="text-sm font-semibold text-slate-800 truncate">{notification.message}</p>
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <span className={`badge capitalize ${colors.badge}`}>{severity}</span>
          <span className={`badge capitalize ${statusCls}`}>{notification.status}</span>
        </div>
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-slate-500 mb-3">
        <div className="flex items-center gap-1">
          <User className="w-3 h-3" />
          <span>{notification.user_id || '—'}</span>
        </div>
        <div className="flex items-center gap-1">
          <Bell className="w-3 h-3" />
          <span>{notification.notification_type || '—'}</span>
        </div>
        <div className="flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          <span>{notification.location_available ? 'Location available' : 'No location'}</span>
        </div>
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{timeAgo(notification.created_at)}</span>
        </div>
      </div>

      {/* Risk score */}
      {notification.risk_score !== undefined && (
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs text-slate-400">Risk Score:</span>
          <div className="flex-1 h-1.5 bg-white rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${colors.bar}`}
              style={{ width: `${notification.risk_score}%` }}
            />
          </div>
          <span className={`text-xs font-bold ${colors.text}`}>{notification.risk_score}/100</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 flex-wrap">
        {!isAcknowledged && !isResolved && (
          <button
            onClick={() => onAcknowledge?.(notification.id)}
            disabled={isLoading}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            Acknowledge
          </button>
        )}
        {!isResolved && (
          <button
            onClick={() => onResolve?.(notification.id)}
            disabled={isLoading}
            className="btn-success text-xs py-1.5 px-3"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            Resolve
          </button>
        )}
        {isResolved && (
          <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
            <CheckCircle className="w-3.5 h-3.5" />
            Resolved
          </span>
        )}
        <span className="text-xs text-slate-400 ml-auto">#{notification.id} · {notification.recipient}</span>
      </div>
    </div>
  );
}
