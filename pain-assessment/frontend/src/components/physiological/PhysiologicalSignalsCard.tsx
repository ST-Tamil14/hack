import React from 'react';
import { Activity, Heart, Wind, Thermometer, ShieldAlert, Zap } from 'lucide-react';
import { PhysiologicalData } from '../../types';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

interface PhysiologicalSignalsCardProps {
  data?: PhysiologicalData;
  history?: Array<{ time: string; hr: number; resp: number }>;
}

export const PhysiologicalSignalsCard: React.FC<PhysiologicalSignalsCardProps> = ({ data, history }) => {
  const defaultData: PhysiologicalData = data || {
    heart_rate_bpm: 82,
    hrv_rmssd_ms: 44,
    respiratory_rate_bpm: 18,
    eda_microsiemens: 2.8,
    skin_temperature_c: 34.8,
    spo2_percent: 98,
    systolic_bp_mmhg: 124,
    diastolic_bp_mmhg: 82,
    pulse_waveform_sample: [0.1, 0.4, 0.9, 0.6, 0.2, 0.1, 0.3, 0.8, 0.5, 0.1],
    signal_quality_score: 0.91,
    is_camera_estimate: true,
    is_reference_sensor: false,
  };

  const chartData = history || [
    { time: '08:00', hr: 74, resp: 15 },
    { time: '08:05', hr: 76, resp: 16 },
    { time: '08:10', hr: 81, resp: 18 },
    { time: '08:15', hr: 85, resp: 19 },
    { time: '08:20', hr: 82, resp: 18 },
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center border border-rose-100">
            <Heart className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-900">Physiological Signals</h3>
              <span className="text-[10px] font-semibold bg-cyan-50 text-cyan-700 px-2 py-0.5 rounded-full border border-cyan-200">
                Camera-based estimate
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Optical rPPG + Skin Perfusion Spectrum</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[10px] text-slate-400 font-semibold uppercase">Signal Quality</div>
          <div className="text-xs font-bold text-emerald-600">
            {Math.round(defaultData.signal_quality_score * 100)}% SNR
          </div>
        </div>
      </div>

      {/* Main Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Heart Rate */}
        <div className="bg-rose-50/50 border border-rose-100 p-3 rounded-xl">
          <div className="flex items-center justify-between text-rose-700 text-xs font-medium mb-1">
            <span>Heart Rate</span>
            <Heart className="w-3.5 h-3.5" />
          </div>
          <div className="text-xl font-bold text-slate-900">
            {defaultData.heart_rate_bpm} <span className="text-xs font-normal text-slate-500">BPM</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">rPPG pulse extraction</div>
        </div>

        {/* Respiratory Rate */}
        <div className="bg-sky-50/50 border border-sky-100 p-3 rounded-xl">
          <div className="flex items-center justify-between text-sky-700 text-xs font-medium mb-1">
            <span>Respiration</span>
            <Wind className="w-3.5 h-3.5" />
          </div>
          <div className="text-xl font-bold text-slate-900">
            {defaultData.respiratory_rate_bpm} <span className="text-xs font-normal text-slate-500">br/min</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Chest motion optical</div>
        </div>

        {/* HRV RMSSD */}
        <div className="bg-emerald-50/50 border border-emerald-100 p-3 rounded-xl">
          <div className="flex items-center justify-between text-emerald-700 text-xs font-medium mb-1">
            <span>HRV RMSSD</span>
            <Activity className="w-3.5 h-3.5" />
          </div>
          <div className="text-xl font-bold text-slate-900">
            {defaultData.hrv_rmssd_ms} <span className="text-xs font-normal text-slate-500">ms</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Autonomic stability</div>
        </div>

        {/* Skin Temp / Perfusion */}
        <div className="bg-amber-50/50 border border-amber-100 p-3 rounded-xl">
          <div className="flex items-center justify-between text-amber-700 text-xs font-medium mb-1">
            <span>Skin Perfusion</span>
            <Thermometer className="w-3.5 h-3.5" />
          </div>
          <div className="text-xl font-bold text-slate-900">
            {defaultData.eda_microsiemens} <span className="text-xs font-normal text-slate-500">μS</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Electrodermal response</div>
        </div>
      </div>

      {/* Historical Heart Rate Chart */}
      <div className="pt-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-2">
          <span>Heart Rate & Respiration Trend</span>
          <span className="text-[10px] text-slate-400">Last 20 minutes</span>
        </div>
        <div className="h-28 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={10} domain={['dataMin - 5', 'dataMax + 5']} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="hr" stroke="#f43f5e" strokeWidth={2} dot={false} name="HR (BPM)" />
              <Line type="monotone" dataKey="resp" stroke="#0284c7" strokeWidth={1.5} dot={false} name="Resp Rate" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Experimental Signals Notice */}
      <div className="bg-slate-50 border border-slate-200/60 p-2.5 rounded-lg flex items-start space-x-2 text-[11px] text-slate-600">
        <ShieldAlert className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-800">Experimental Camera Estimates:</span> SpO₂ ({defaultData.spo2_percent}%) & Blood Pressure ({defaultData.systolic_bp_mmhg}/{defaultData.diastolic_bp_mmhg} mmHg) are unvalidated camera approximations and are not used for clinical treatment decisions without a validated cuff/sensor.
        </div>
      </div>
    </div>
  );
};
