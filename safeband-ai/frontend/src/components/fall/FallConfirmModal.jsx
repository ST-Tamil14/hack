import { AlertTriangle, CheckCircle, HelpCircle, X, Clock } from 'lucide-react';
import { useState, useEffect } from 'react';
import { formatDateTime } from '../../utils/formatDate';

const COUNTDOWN_SECONDS = 30;

export default function FallConfirmModal({ detectedAt, onSafe, onConfirm, onUnableToRespond, onDismiss }) {
  const [secondsLeft, setSecondsLeft] = useState(COUNTDOWN_SECONDS);

  useEffect(() => {
    if (secondsLeft <= 0) {
      onUnableToRespond?.();
      return;
    }
    const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [secondsLeft]);

  const pct = (secondsLeft / COUNTDOWN_SECONDS) * 100;
  const circumference = 2 * Math.PI * 28;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md fade-in border-2 border-orange-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <p className="font-bold text-slate-800 text-lg">Possible Fall Detected</p>
          </div>
          <button onClick={onDismiss} className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 pb-5">
          <p className="text-slate-600 text-sm mb-4">
            Our AI model detected a possible fall event. Please confirm your status.
          </p>

          {/* Detected time */}
          {detectedAt && (
            <div className="flex items-center gap-2 text-xs text-slate-500 mb-4 bg-orange-50 px-3 py-2 rounded-lg border border-orange-100">
              <Clock className="w-3.5 h-3.5 text-orange-400" />
              <span>Detected at: {formatDateTime(detectedAt)}</span>
            </div>
          )}

          {/* Countdown ring */}
          <div className="flex justify-center mb-5">
            <div className="relative w-20 h-20">
              <svg className="w-20 h-20 -rotate-90" viewBox="0 0 64 64">
                <circle cx="32" cy="32" r="28" fill="none" stroke="#f1f5f9" strokeWidth="6" />
                <circle
                  cx="32" cy="32" r="28"
                  fill="none"
                  stroke={secondsLeft > 10 ? '#ea580c' : '#dc2626'}
                  strokeWidth="6"
                  strokeDasharray={circumference}
                  strokeDashoffset={circumference * (1 - pct / 100)}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-2xl font-bold ${secondsLeft <= 10 ? 'text-red-600' : 'text-orange-600'}`}>
                  {secondsLeft}
                </span>
                <span className="text-[9px] text-slate-400">seconds</span>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-2.5">
            <button
              onClick={onSafe}
              className="btn-success w-full justify-center py-3"
            >
              <CheckCircle className="w-4 h-4" />
              I am Safe
            </button>
            <button
              onClick={onConfirm}
              className="btn-danger w-full justify-center py-3"
            >
              <AlertTriangle className="w-4 h-4" />
              Confirm Fall
            </button>
            <button
              onClick={onUnableToRespond}
              className="btn-warning w-full justify-center py-3"
            >
              <HelpCircle className="w-4 h-4" />
              Unable to Respond
            </button>
          </div>

          <p className="text-[10px] text-slate-400 text-center mt-3">
            If no response is received, emergency alert will be sent automatically.
          </p>
        </div>
      </div>
    </div>
  );
}
