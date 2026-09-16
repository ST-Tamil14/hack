import React from 'react';
import { Shield, AlertCircle, CheckCircle2, UserX } from 'lucide-react';
import { BehavioralData } from '../../types';

interface BehavioralAnalysisCardProps {
  data?: BehavioralData;
}

export const BehavioralAnalysisCard: React.FC<BehavioralAnalysisCardProps> = ({ data }) => {
  const defaultData: BehavioralData = data || {
    restlessness_level: 'moderate',
    guarding_detected: true,
    unusual_stillness: false,
    posture_abnormality_score: 0.45,
    mobility_reduction_score: 0.6,
    agitation_score: 0.32,
    behavioral_pain_score: 54,
    confidence: 0.88,
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center border border-purple-100">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Behavioral & Postural Analysis</h3>
            <p className="text-[11px] text-slate-500">Gross body movement & guarding classification</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[10px] text-slate-400 font-semibold uppercase">Behavior Score</div>
          <div className="text-base font-bold text-purple-700">{defaultData.behavioral_pain_score}/100</div>
        </div>
      </div>

      {/* Primary Behavioral Event Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        {/* Restlessness */}
        <div className="bg-slate-50 border border-slate-100 p-2.5 rounded-lg flex items-center justify-between">
          <span className="text-slate-600">Restlessness:</span>
          <span className="font-semibold capitalize text-purple-700 bg-purple-50 px-2 py-0.5 rounded-md border border-purple-200">
            {defaultData.restlessness_level}
          </span>
        </div>

        {/* Guarding */}
        <div className="bg-slate-50 border border-slate-100 p-2.5 rounded-lg flex items-center justify-between">
          <span className="text-slate-600">Protective Guarding:</span>
          {defaultData.guarding_detected ? (
            <span className="flex items-center space-x-1 font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200">
              <AlertCircle className="w-3 h-3" />
              <span>Detected</span>
            </span>
          ) : (
            <span className="flex items-center space-x-1 font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
              <CheckCircle2 className="w-3 h-3" />
              <span>Normal</span>
            </span>
          )}
        </div>
      </div>

      {/* Quantitative Behavioral Feature Bars */}
      <div className="space-y-2 text-xs">
        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Posture Abnormality Index</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.posture_abnormality_score * 100)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500 rounded-full"
              style={{ width: `${defaultData.posture_abnormality_score * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Mobility Reduction Score</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.mobility_reduction_score * 100)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500 rounded-full"
              style={{ width: `${defaultData.mobility_reduction_score * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
