import React, { useState } from 'react';
import { Eye, ChevronDown, ChevronUp, UserCheck, Sparkles } from 'lucide-react';
import { FacialAnalysisData } from '../../types';

interface FacialAnalysisCardProps {
  data?: FacialAnalysisData;
}

export const FacialAnalysisCard: React.FC<FacialAnalysisCardProps> = ({ data }) => {
  const [expanded, setExpanded] = useState(false);

  const defaultData: FacialAnalysisData = data || {
    face_detected: true,
    face_count: 1,
    confidence: 0.94,
    brow_movement: 0.65,
    eye_narrowing: 0.58,
    nose_wrinkling: 0.42,
    mouth_movement: 0.35,
    facial_tension: 0.68,
    blink_frequency_bpm: 18,
    head_movement_index: 0.22,
    facial_pain_score: 62,
    quality_weight: 0.92,
  };

  const getScoreColor = (score: number) => {
    if (score < 35) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score < 65) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-rose-600 bg-rose-50 border-rose-200';
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100">
            <Eye className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-900">Facial Expressive Analysis</h3>
              <span className="text-[10px] font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                Camera AI
              </span>
            </div>
            <p className="text-[11px] text-slate-500">MediaPipe landmark AU motion vectoring</p>
          </div>
        </div>

        {/* Score Badge */}
        <div className={`px-3 py-1 rounded-lg border text-right ${getScoreColor(defaultData.facial_pain_score)}`}>
          <div className="text-[10px] uppercase font-bold tracking-wider opacity-80">Pain Index</div>
          <div className="text-lg font-bold leading-none">{defaultData.facial_pain_score}/100</div>
        </div>
      </div>

      {/* Face Status Bar */}
      <div className="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100">
        <div className="flex items-center space-x-2">
          <UserCheck className={`w-4 h-4 ${defaultData.face_detected ? 'text-emerald-500' : 'text-slate-400'}`} />
          <span className="font-medium text-slate-700">
            {defaultData.face_detected ? `Face Tracked (${defaultData.face_count})` : 'Searching for Face...'}
          </span>
        </div>
        <div className="text-slate-500">
          Confidence: <span className="font-semibold text-slate-800">{Math.round(defaultData.confidence * 100)}%</span>
        </div>
      </div>

      {/* Primary Facial Features Progress Bars */}
      <div className="space-y-2 text-xs">
        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Brow Movement (Corrugator AU4)</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.brow_movement * 100)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${defaultData.brow_movement * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Orbital Eye Narrowing (Orbicularis AU6/7)</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.eye_narrowing * 100)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${defaultData.eye_narrowing * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Nose Wrinkling (Levator AU9)</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.nose_wrinkling * 100)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${defaultData.nose_wrinkling * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Expandable Details Toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-xs text-slate-500 hover:text-slate-800 pt-1 font-medium"
      >
        <span>{expanded ? 'Hide Action Unit Details' : 'Show Action Unit Details'}</span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {expanded && (
        <div className="pt-2 border-t border-slate-100 space-y-2 text-xs text-slate-600 bg-slate-50/50 p-2.5 rounded-lg">
          <div className="flex justify-between">
            <span>Mouth Corner Tension:</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.mouth_movement * 100)}%</span>
          </div>
          <div className="flex justify-between">
            <span>Facial Muscle Mass Tension:</span>
            <span className="font-semibold text-slate-800">{Math.round(defaultData.facial_tension * 100)}%</span>
          </div>
          <div className="flex justify-between">
            <span>Blink Frequency:</span>
            <span className="font-semibold text-slate-800">{defaultData.blink_frequency_bpm} / min</span>
          </div>
          <div className="flex justify-between">
            <span>Head Tilt Instability:</span>
            <span className="font-semibold text-slate-800">{defaultData.head_movement_index}</span>
          </div>
        </div>
      )}
    </div>
  );
};
