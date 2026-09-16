import { AlertTriangle, Bell, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function EmergencyBanner({ count, onDismiss }) {
  const navigate = useNavigate();
  if (!count || count === 0) return null;

  return (
    <div className="bg-red-600 text-white px-4 py-3 flex items-center gap-3 fade-in">
      <AlertTriangle className="w-5 h-5 flex-shrink-0 animate-bounce" />
      <div className="flex-1">
        <p className="text-sm font-bold">
          {count} Active Emergency Alert{count > 1 ? 's' : ''}
        </p>
        <p className="text-xs text-red-200">Immediate caregiver attention required</p>
      </div>
      <button
        onClick={() => navigate('/alerts')}
        className="flex-shrink-0 text-xs bg-white text-red-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
      >
        View Alerts
      </button>
      {onDismiss && (
        <button onClick={onDismiss} className="flex-shrink-0 p-1 rounded hover:bg-red-700 transition-colors">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
