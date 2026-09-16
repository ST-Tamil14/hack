import { useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

const styles = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error:   'bg-red-50 border-red-200 text-red-800',
  info:    'bg-blue-50 border-blue-200 text-blue-800',
  warning: 'bg-orange-50 border-orange-200 text-orange-800',
};

function Toast({ id, message, variant = 'success' }) {
  const { dispatch } = useApp();
  const Icon = icons[variant] || Info;

  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg max-w-sm slide-in-right ${styles[variant] || styles.info}`}>
      <Icon className="w-4 h-4 flex-shrink-0 mt-0.5" />
      <p className="text-sm font-medium flex-1">{message}</p>
      <button
        onClick={() => dispatch({ type: 'REMOVE_TOAST', payload: id })}
        className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const { state } = useApp();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {state.toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast {...toast} />
        </div>
      ))}
    </div>
  );
}
