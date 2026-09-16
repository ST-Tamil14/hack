import React, { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { FileText, ArrowLeft, CheckCircle, Clock, ShieldCheck, Printer, Download } from 'lucide-react';
import { MultimodalFusionCard } from '../components/assessment/MultimodalFusionCard';
import { FacialAnalysisCard } from '../components/facial/FacialAnalysisCard';
import { PhysiologicalSignalsCard } from '../components/physiological/PhysiologicalSignalsCard';

export const SessionDetails: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id') || 'sess-1001';
  const [notes, setNotes] = useState('Patient reported 7/10 incisional pain post-hip replacement. Administered 5mg IV Morphine at 08:25.');
  const [saved, setSaved] = useState(false);

  const handleSaveNotes = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link to="/" className="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-cyan-600 font-medium">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Overview Dashboard</span>
      </Link>

      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-900">Session Review: {sessionId}</h1>
            <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold px-2.5 py-0.5 rounded-full">
              Completed
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Patient: Eleanor Vance (PAT-8801) • Recorded 2026-09-09 08:15 - 08:30 AM
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            to={`/reports?session_id=${sessionId}`}
            className="px-4 py-2 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 rounded-xl transition-all shadow-xs flex items-center space-x-1.5"
          >
            <FileText className="w-4 h-4" />
            <span>Generate Official Clinical Report</span>
          </Link>
        </div>
      </div>

      {/* Main Analysis Summary */}
      <MultimodalFusionCard />

      {/* Modality Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FacialAnalysisCard />
        <PhysiologicalSignalsCard />
      </div>

      {/* Clinician Notes Section */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-3">
        <h3 className="text-sm font-bold text-slate-900">Attending Clinician Notes & Medication Log</h3>
        <textarea
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full p-3 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 text-slate-800"
          placeholder="Enter clinical observations, intervention response, or medication log..."
        />

        <div className="flex items-center justify-between">
          {saved ? (
            <span className="text-xs font-semibold text-emerald-600 flex items-center space-x-1">
              <CheckCircle className="w-4 h-4" />
              <span>Notes updated successfully!</span>
            </span>
          ) : (
            <span className="text-[11px] text-slate-400">All modifications are logged for audit compliance.</span>
          )}

          <button
            onClick={handleSaveNotes}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer"
          >
            Save Notes
          </button>
        </div>
      </div>
    </div>
  );
};
