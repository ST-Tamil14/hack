/**
 * A small colored badge pill for status, severity, etc.
 */
export default function StatusBadge({ label, variant = 'default', className = '' }) {
  const variants = {
    default:      'bg-slate-100 text-slate-600 border-slate-200',
    online:       'bg-green-100 text-green-700 border-green-200',
    offline:      'bg-red-100 text-red-700 border-red-200',
    warning:      'bg-orange-100 text-orange-700 border-orange-200',
    info:         'bg-blue-100 text-blue-700 border-blue-200',
    success:      'bg-green-100 text-green-700 border-green-200',
    danger:       'bg-red-100 text-red-700 border-red-200',
    critical:     'bg-red-100 text-red-700 border-red-200',
    high:         'bg-orange-100 text-orange-700 border-orange-200',
    medium:       'bg-yellow-100 text-yellow-700 border-yellow-200',
    low:          'bg-green-100 text-green-700 border-green-200',
    normal:       'bg-green-100 text-green-700 border-green-200',
    simulated:    'bg-slate-100 text-slate-600 border-slate-200',
    sent:         'bg-blue-100 text-blue-700 border-blue-200',
    acknowledged: 'bg-cyan-100 text-cyan-700 border-cyan-200',
    resolved:     'bg-green-100 text-green-700 border-green-200',
    failed:       'bg-red-100 text-red-700 border-red-200',
    fall:         'bg-red-100 text-red-700 border-red-200',
    'no-fall':    'bg-green-100 text-green-700 border-green-200',
  };

  return (
    <span className={`badge ${variants[variant] || variants.default} ${className}`}>
      {label}
    </span>
  );
}
