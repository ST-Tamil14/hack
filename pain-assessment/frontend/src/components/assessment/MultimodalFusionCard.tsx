import React from 'react';
import { Activity, ShieldAlert, Sparkles, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { MultimodalAssessmentResult } from '../../types';

interface MultimodalFusionCardProps {
  data?: MultimodalAssessmentResult;
}

export const MultimodalFusionCard: React.FC<MultimodalFusionCardProps> = ({ data }) => {
  const defaultData: MultimodalAssessmentResult = data || {
    overall_pain_score: 68,
    pain_level: 'high',
    ai_confidence: 89,
    signal_quality: 92,
    facial_contribution: 35,
    physiological_contribution: 30,
    behavioral_contribution: 20,
    voice_contribution: 15,
    contributing_factors: [
      'Elevated brow furrowing & orbital tightening (Action Units 4/7)',
      'Autonomic heart rate elevation (+12 BPM over baseline)',
      'Vocalized sighing & acoustic pitch instability detected',
      'Guarding posture & restlessness identified',
    ],
    disclaimer:
      'AI-assisted assessment: Results are estimates intended to support clinical review. They are not a substitute for validated medical measurements or professional medical diagnosis.',
    needs_clinical_review: true,
    timestamp: new Date().toISOString(),
  };

  const getScoreBadge = (score: number) => {
    if (score < 35) {
      return {
        label: 'Low / Mild Distress',
        color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
        ring: 'border-emerald-500',
      };
    }
    if (score < 65) {
      return {
        label: 'Moderate Pain-Distress',
        color: 'text-amber-700 bg-amber-50 border-amber-200',
        ring: 'border-amber-500',
      };
    }
    return {
      label: 'High Pain-Distress',
      color: 'text-rose-700 bg-rose-50 border-rose-200',
      ring: 'border-rose-500',
    };
  };

  const badge = getScoreBadge(defaultData.overall_pain_score);

  return (
    <div className="bg-white rounded-xl border-2 border-slate-200 p-5 shadow-sm space-y-5">
      {/* Top Title & AI Status */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-500 text-white flex items-center justify-center shadow-xs">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Multimodal AI Pain Estimation</h2>
            <p className="text-xs text-slate-500">Profile-Aware Fusion across 4 Sensor Channels</p>
          </div>
        </div>

        {defaultData.needs_clinical_review && (
          <span className="flex items-center space-x-1 text-xs font-bold text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Needs Clinical Review</span>
          </span>
        )}
      </div>

      {/* Hero Score Display */}
      <div className="flex flex-col sm:flex-row items-center justify-between bg-slate-50 p-4 rounded-xl border border-slate-200/80 gap-4">
        {/* Score Ring */}
        <div className="flex items-center space-x-4">
          <div className={`w-20 h-20 rounded-full border-4 ${badge.ring} bg-white flex flex-col items-center justify-center shadow-xs`}>
            <span className="text-2xl font-black text-slate-900 leading-none">{defaultData.overall_pain_score}</span>
            <span className="text-[10px] text-slate-400 font-semibold uppercase">/ 100</span>
          </div>

          <div>
            <div className={`inline-block px-2.5 py-0.5 rounded-md border text-xs font-bold ${badge.color} mb-1`}>
              {badge.label}
            </div>
            <div className="text-xs text-slate-600 space-x-3">
              <span>AI Confidence: <strong className="text-slate-900">{defaultData.ai_confidence}%</strong></span>
              <span>•</span>
              <span>Signal Quality: <strong className="text-slate-900">{defaultData.signal_quality}%</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Modality Weights Breakdown */}
      <div>
        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
          Profile-Weighted Modality Contributions
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          <div className="bg-indigo-50/60 border border-indigo-100 p-2.5 rounded-lg">
            <div className="text-[11px] text-indigo-700 font-medium">Facial Expressive</div>
            <div className="text-lg font-bold text-slate-900">{defaultData.facial_contribution}%</div>
          </div>
          <div className="bg-rose-50/60 border border-rose-100 p-2.5 rounded-lg">
            <div className="text-[11px] text-rose-700 font-medium">Physiological rPPG</div>
            <div className="text-lg font-bold text-slate-900">{defaultData.physiological_contribution}%</div>
          </div>
          <div className="bg-purple-50/60 border border-purple-100 p-2.5 rounded-lg">
            <div className="text-[11px] text-purple-700 font-medium">Behavioral Posture</div>
            <div className="text-lg font-bold text-slate-900">{defaultData.behavioral_contribution}%</div>
          </div>
          <div className="bg-teal-50/60 border border-teal-100 p-2.5 rounded-lg">
            <div className="text-[11px] text-teal-700 font-medium">Voice & Sound</div>
            <div className="text-lg font-bold text-slate-900">{defaultData.voice_contribution}%</div>
          </div>
        </div>
      </div>

      {/* Key Contributing Clinical Factors */}
      <div>
        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
          Key Contributing Observations
        </h4>
        <ul className="space-y-1.5 text-xs text-slate-700">
          {defaultData.contributing_factors.map((factor, idx) => (
            <li key={idx} className="flex items-start space-x-2">
              <CheckCircle className="w-3.5 h-3.5 text-teal-600 flex-shrink-0 mt-0.5" />
              <span>{factor}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Mandatory Disclaimer */}
      <div className="bg-amber-50/70 border border-amber-200/80 p-3 rounded-lg flex items-start space-x-2 text-[11px] text-amber-900">
        <Info className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">{defaultData.disclaimer}</p>
      </div>
    </div>
  );
};
