import { formatSensorValue } from '../../utils/formatSensorValue';

/**
 * Displays a single sensor reading in a compact card.
 */
export default function SensorCard({ label, value, unit = '', decimals = 3, color = 'brand', className = '' }) {
  const colorMap = {
    brand:  { bg: 'bg-brand-50',  dot: 'bg-brand-500',  text: 'text-brand-700' },
    blue:   { bg: 'bg-blue-50',   dot: 'bg-blue-500',   text: 'text-blue-700' },
    purple: { bg: 'bg-purple-50', dot: 'bg-purple-500', text: 'text-purple-700' },
    green:  { bg: 'bg-green-50',  dot: 'bg-green-500',  text: 'text-green-700' },
    red:    { bg: 'bg-red-50',    dot: 'bg-red-500',    text: 'text-red-700' },
    orange: { bg: 'bg-orange-50', dot: 'bg-orange-500', text: 'text-orange-700' },
    slate:  { bg: 'bg-slate-50',  dot: 'bg-slate-400',  text: 'text-slate-600' },
  };
  const c = colorMap[color] || colorMap.brand;

  const displayValue =
    value === null || value === undefined
      ? '—'
      : formatSensorValue(value, decimals, '');

  return (
    <div className={`flex items-center justify-between p-3 rounded-lg border border-slate-100 ${c.bg} ${className}`}>
      <div className="flex items-center gap-2">
        <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${c.dot}`} />
        <span className="text-xs font-medium text-slate-600 leading-tight">{label}</span>
      </div>
      <div className="text-right">
        <span className={`text-sm font-bold ${c.text}`}>{displayValue}</span>
        {unit && <span className="text-xs text-slate-400 ml-1">{unit}</span>}
      </div>
    </div>
  );
}
