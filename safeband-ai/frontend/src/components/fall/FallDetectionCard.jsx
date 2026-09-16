import { Shield, AlertTriangle, CheckCircle, Info, Brain } from 'lucide-react';
import StatusBadge from '../ui/StatusBadge';
import { timeAgo } from '../../utils/formatDate';

function ConfidenceBar({ value, threshold }) {
  const pct = ((value || 0) * 100).toFixed(1);
  const threshPct = ((threshold || 0.5) * 100).toFixed(1);
  const overThreshold = value >= (threshold || 0.5);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-500">Confidence</span>
        <span className={`font-bold ${overThreshold ? 'text-red-600' : 'text-slate-700'}`}>{pct}%</span>
      </div>
      <div className="relative h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${overThreshold ? 'bg-red-500' : 'bg-green-500'}`}
          style={{ width: `${pct}%` }}
        />
        {/* Threshold marker */}
        <div
          className="absolute top-0 h-full w-0.5 bg-slate-400"
          style={{ left: `${threshPct}%` }}
          title={`Threshold: ${threshPct}%`}
        />
      </div>
      <p className="text-[10px] text-slate-400">Threshold: {threshPct}%</p>
    </div>
  );
}

export default function FallDetectionCard({ mlDetection, confirmation, lastUpdated }) {
  if (!mlDetection) {
    return (
      <div className="card p-5">
        <p className="section-title mb-1">AI Fall Detection</p>
        <p className="text-sm text-slate-400">Waiting for ML model results…</p>
      </div>
    );
  }

  const fallDetected = mlDetection.model_detected_fall || mlDetection.fall_detected;
  const confirmed = confirmation?.confirmed;
  const confidence = mlDetection.confidence;
  const threshold = mlDetection.confidence_threshold || 0.5;
  const status = mlDetection.status || (fallDetected ? 'fall_detected' : 'normal');

  let statusLabel = 'Normal';
  let StatusIcon = CheckCircle;
  let cardStyle = 'bg-green-50 border-green-200';
  let iconColor = 'text-green-600';

  if (fallDetected && confirmed) {
    statusLabel = 'Confirmed Fall';
    StatusIcon = AlertTriangle;
    cardStyle = 'bg-red-50 border-red-200';
    iconColor = 'text-red-600';
  } else if (fallDetected) {
    statusLabel = 'Possible Fall';
    StatusIcon = AlertTriangle;
    cardStyle = 'bg-orange-50 border-orange-200';
    iconColor = 'text-orange-600';
  }

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-brand-600" />
          <p className="section-title">AI Fall Detection</p>
        </div>
        <StatusBadge
          label={statusLabel}
          variant={fallDetected && confirmed ? 'danger' : fallDetected ? 'warning' : 'success'}
        />
      </div>

      {/* Status panel */}
      <div className={`flex items-center gap-3 p-4 rounded-xl border mb-4 ${cardStyle}`}>
        <StatusIcon className={`w-8 h-8 flex-shrink-0 ${iconColor}`} />
        <div>
          <p className={`font-bold text-lg ${iconColor}`}>{statusLabel}</p>
          <p className="text-xs text-slate-500">
            {fallDetected && confirmed
              ? 'Fall has been confirmed. Emergency notification sent.'
              : fallDetected
              ? 'Model detected a possible fall. Awaiting confirmation.'
              : 'No fall detected. User appears safe.'}
          </p>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="mb-4">
        <ConfidenceBar value={confidence} threshold={threshold} />
      </div>

      {/* Detection details */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
          <p className="text-slate-400 mb-0.5">Model Prediction</p>
          <p className="font-semibold text-slate-700">{mlDetection.prediction === 1 ? 'Fall' : 'No Fall'}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
          <p className="text-slate-400 mb-0.5">User Confirmation</p>
          <p className="font-semibold text-slate-700">
            {confirmation?.user_response === 'confirmed' ? 'Confirmed Fall'
              : confirmation?.user_response === 'safe' ? 'User is Safe'
              : 'Not Confirmed'}
          </p>
        </div>
        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
          <p className="text-slate-400 mb-0.5">Model Status</p>
          <p className="font-semibold text-slate-700 capitalize">{(status || 'normal').replace(/_/g, ' ')}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100">
          <p className="text-slate-400 mb-0.5">Last Detection</p>
          <p className="font-semibold text-slate-700">{timeAgo(lastUpdated)}</p>
        </div>
      </div>
    </div>
  );
}
