import { Shield, AlertTriangle, Heart, Wind, Info } from 'lucide-react';
import { getSeverityColors } from '../../utils/riskHelpers';
import { formatRiskScore } from '../../utils/formatSensorValue';

function RiskGauge({ score }) {
  const clamped = Math.max(0, Math.min(100, score || 0));
  const circumference = 2 * Math.PI * 40;
  const dashOffset = circumference * (1 - clamped / 100);

  const color =
    clamped >= 75 ? '#dc2626' :
    clamped >= 50 ? '#ea580c' :
    clamped >= 25 ? '#f59e0b' :
    '#16a34a';

  return (
    <div className="relative w-28 h-28 mx-auto">
      <svg className="w-28 h-28 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r="40" fill="none" stroke="#f1f5f9" strokeWidth="8" />
        <circle
          cx="48" cy="48" r="40"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-slate-800">{Math.round(clamped)}</span>
        <span className="text-[10px] text-slate-400">/ 100</span>
      </div>
    </div>
  );
}

export default function SeverityCard({ severity }) {
  if (!severity) {
    return (
      <div className="card p-5">
        <p className="section-title mb-1">Fall Severity Analysis</p>
        <p className="text-sm text-slate-400">No severity data available.</p>
        <p className="disclaimer">Prototype risk estimate; not a clinical diagnosis.</p>
      </div>
    );
  }

  const level = (severity.severity || 'low').toLowerCase();
  const colors = getSeverityColors(level);
  const riskScore = severity.risk_score ?? 0;
  const reasons = severity.risk_reasons || [];

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-brand-600" />
          <p className="section-title">Fall Severity Analysis</p>
        </div>
        <span className={`badge ${colors.badge} capitalize`}>{level}</span>
      </div>

      {/* Risk gauge */}
      <div className="mb-4">
        <RiskGauge score={riskScore} />
        <p className="text-center text-xs text-slate-500 mt-1">Risk Score: {formatRiskScore(riskScore)}</p>
      </div>

      {/* Risk factors grid */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {severity.fall_probability !== undefined && (
          <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-xs">
            <p className="text-slate-400">Fall Probability</p>
            <p className="font-bold text-slate-700">{(severity.fall_probability * 100).toFixed(1)}%</p>
          </div>
        )}
        {severity.acceleration_magnitude !== undefined && (
          <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-xs">
            <p className="text-slate-400">Impact Intensity</p>
            <p className="font-bold text-slate-700">{severity.acceleration_magnitude?.toFixed(2)} m/s²</p>
          </div>
        )}
        {severity.inactivity_seconds !== undefined && (
          <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-xs">
            <p className="text-slate-400">Post-Fall Inactivity</p>
            <p className="font-bold text-slate-700">{severity.inactivity_seconds}s</p>
          </div>
        )}
        {severity.location_available !== undefined && (
          <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-xs">
            <p className="text-slate-400">Location</p>
            <p className={`font-bold ${severity.location_available ? 'text-green-600' : 'text-slate-500'}`}>
              {severity.location_available ? 'Available' : 'Unavailable'}
            </p>
          </div>
        )}
        {severity.heart_rate_warning !== undefined && (
          <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-xs">
            <p className="text-slate-400 flex items-center gap-1"><Heart className="w-3 h-3" />HR Warning</p>
            <p className={`font-bold ${severity.heart_rate_warning ? 'text-orange-600' : 'text-green-600'}`}>
              {severity.heart_rate_warning ? 'Abnormal' : 'Normal'}
            </p>
          </div>
        )}
        {severity.spo2_warning !== undefined && (
          <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 text-xs">
            <p className="text-slate-400 flex items-center gap-1"><Wind className="w-3 h-3" />SpO2 Warning</p>
            <p className={`font-bold ${severity.spo2_warning ? 'text-orange-600' : 'text-green-600'}`}>
              {severity.spo2_warning ? 'Low SpO2' : 'Normal'}
            </p>
          </div>
        )}
      </div>

      {/* Risk reasons */}
      {reasons.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wide">Risk Factors</p>
          <ul className="space-y-1">
            {reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-1.5 text-xs text-slate-600">
                <span className={`w-1.5 h-1.5 rounded-full mt-1 flex-shrink-0 ${colors.dot}`} />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="disclaimer flex items-center gap-1">
        <Info className="w-3 h-3" />
        Prototype risk estimate; not a clinical diagnosis.
      </p>
    </div>
  );
}
