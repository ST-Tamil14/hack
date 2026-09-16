import React from 'react';
import { Volume2, Mic, AlertCircle, Music } from 'lucide-react';
import { VoiceAnalysisData } from '../../types';

interface VoiceAnalysisCardProps {
  data?: VoiceAnalysisData;
}

export const VoiceAnalysisCard: React.FC<VoiceAnalysisCardProps> = ({ data }) => {
  const defaultData: VoiceAnalysisData = data || {
    microphone_active: true,
    pitch_hz: 215,
    loudness_db: 58,
    jitter_percent: 1.82,
    shimmer_percent: 4.15,
    hnr_db: 18.5,
    vocal_distress_detected: true,
    crying_detected: false,
    moaning_detected: true,
    groaning_detected: false,
    sighing_detected: true,
    audio_pain_score: 48,
    confidence: 0.86,
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center border border-teal-100">
            <Volume2 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-900">Acoustic Voice & Sound Analysis</h3>
              <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full border border-emerald-200">
                Mic Active
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Spectral pitch, Jitter/Shimmer, and vocalizations</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[10px] text-slate-400 font-semibold uppercase">Voice Index</div>
          <div className="text-base font-bold text-teal-700">{defaultData.audio_pain_score}/100</div>
        </div>
      </div>

      {/* Detected Acoustic Events */}
      <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg space-y-2 text-xs">
        <div className="flex items-center justify-between font-medium text-slate-700">
          <span>Vocal Pain Expressions:</span>
          {defaultData.vocal_distress_detected ? (
            <span className="text-rose-600 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200 font-bold flex items-center space-x-1">
              <AlertCircle className="w-3 h-3" />
              <span>Distress Detected</span>
            </span>
          ) : (
            <span className="text-emerald-600">Quiet / Normal</span>
          )}
        </div>

        <div className="flex flex-wrap gap-1.5 pt-1">
          {defaultData.moaning_detected && (
            <span className="bg-rose-100 text-rose-800 text-[10px] font-semibold px-2 py-0.5 rounded-md border border-rose-200">
              • Moaning
            </span>
          )}
          {defaultData.sighing_detected && (
            <span className="bg-amber-100 text-amber-800 text-[10px] font-semibold px-2 py-0.5 rounded-md border border-amber-200">
              • Sighing
            </span>
          )}
          {defaultData.crying_detected && (
            <span className="bg-purple-100 text-purple-800 text-[10px] font-semibold px-2 py-0.5 rounded-md border border-purple-200">
              • Crying
            </span>
          )}
          {defaultData.groaning_detected && (
            <span className="bg-orange-100 text-orange-800 text-[10px] font-semibold px-2 py-0.5 rounded-md border border-orange-200">
              • Groaning
            </span>
          )}
          {!defaultData.moaning_detected &&
            !defaultData.sighing_detected &&
            !defaultData.crying_detected &&
            !defaultData.groaning_detected && (
              <span className="text-slate-400 text-[11px]">No abnormal vocalizations detected.</span>
            )}
        </div>
      </div>

      {/* Acoustic Parameters Grid */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
          <div className="text-[10px] text-slate-400">Mean Pitch</div>
          <div className="font-bold text-slate-800">{defaultData.pitch_hz} Hz</div>
        </div>
        <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
          <div className="text-[10px] text-slate-400">Jitter</div>
          <div className="font-bold text-slate-800">{defaultData.jitter_percent}%</div>
        </div>
        <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
          <div className="text-[10px] text-slate-400">HNR Noise</div>
          <div className="font-bold text-slate-800">{defaultData.hnr_db} dB</div>
        </div>
      </div>
    </div>
  );
};
