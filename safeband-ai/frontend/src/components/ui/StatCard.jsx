import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * Reusable stat summary card used across the dashboard.
 */
export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconBg = 'bg-brand-50',
  iconColor = 'text-brand-600',
  trend,          // 'up' | 'down' | 'neutral'
  trendLabel,
  alert = false,  // true = red emergency style
  loading = false,
  className = '',
}) {
  if (loading) {
    return (
      <div className={`card p-4 ${className}`}>
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <div className="h-3 bg-slate-100 rounded animate-pulse w-24" />
            <div className="h-7 bg-slate-100 rounded animate-pulse w-16" />
            <div className="h-3 bg-slate-100 rounded animate-pulse w-32" />
          </div>
          <div className="w-10 h-10 bg-slate-100 rounded-lg animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div
      className={`card p-4 card-hover fade-in
        ${alert ? 'border-red-200 bg-red-50' : ''}
        ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className={`text-xs font-medium uppercase tracking-wide truncate
            ${alert ? 'text-red-500' : 'text-slate-500'}`}>
            {title}
          </p>
          <p className={`mt-1 text-2xl font-bold leading-tight truncate
            ${alert ? 'text-red-700' : 'text-slate-800'}`}>
            {value ?? '—'}
          </p>
          {subtitle && (
            <p className={`mt-1 text-xs truncate ${alert ? 'text-red-500' : 'text-slate-500'}`}>
              {subtitle}
            </p>
          )}
          {trendLabel && (
            <div className={`mt-1.5 flex items-center gap-1 text-xs font-medium
              ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-500' : 'text-slate-400'}`}>
              {trend === 'up' && <TrendingUp className="w-3 h-3" />}
              {trend === 'down' && <TrendingDown className="w-3 h-3" />}
              {trend === 'neutral' && <Minus className="w-3 h-3" />}
              <span>{trendLabel}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center
            ${alert ? 'bg-red-100' : iconBg}`}>
            <Icon className={`w-5 h-5 ${alert ? 'text-red-600' : iconColor}`} />
          </div>
        )}
      </div>
    </div>
  );
}
