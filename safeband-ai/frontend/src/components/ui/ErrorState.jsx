import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorState({ message, onRetry, className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 text-slate-400 ${className}`}>
      <AlertCircle className="w-10 h-10 mb-3 text-red-400" />
      <p className="text-sm font-semibold text-slate-600 mb-1">Something went wrong</p>
      <p className="text-xs text-slate-400 text-center max-w-xs mb-4">
        {message || 'Backend is currently unavailable. Please check the Render service.'}
      </p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-xs">
          <RefreshCw className="w-3.5 h-3.5" />
          Retry
        </button>
      )}
    </div>
  );
}
