import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { Printer, Download, FileCheck, Activity, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const Reports: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id') || 'sess-1001';

  const handlePrint = () => {
    window.print();
  };

  const handleExportCSV = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,SessionID,PatientID,PatientName,PainScore,HeartRate,Respiration,Timestamp\n' +
      `${sessionId},PAT-8801,Eleanor Vance,68,82,18,2026-09-09T08:30:00Z\n`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `pain_assessment_report_${sessionId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Top Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs print:hidden">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Clinical Assessment Report</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Formal document for patient medical records & clinical chart inclusion
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleExportCSV}
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors flex items-center space-x-1.5 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 rounded-xl transition-all shadow-xs flex items-center space-x-2 cursor-pointer"
          >
            <Printer className="w-4 h-4" />
            <span>Print Report (PDF)</span>
          </button>
        </div>
      </div>

      {/* Printable Report Document Card */}
      <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6 print:shadow-none print:border-none print:p-0">
        {/* Hospital / System Header */}
        <div className="flex items-center justify-between border-b-2 border-slate-900 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-cyan-600 text-white flex items-center justify-center font-bold">
              <Activity className="w-7 h-7 stroke-[2.5]" />
            </div>
            <div>
              <h2 className="text-lg font-black text-slate-900 uppercase tracking-tight">PainSense AI Medical Center</h2>
              <p className="text-xs text-slate-500">Multimodal Clinical Pain Assessment & Monitoring Service</p>
            </div>
          </div>

          <div className="text-right text-xs text-slate-600">
            <div className="font-bold text-slate-900">Session ID: {sessionId}</div>
            <div>Report Date: {new Date().toLocaleDateString()}</div>
          </div>
        </div>

        {/* Patient Demographics Table */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Patient Name</div>
            <div className="font-bold text-slate-900">Eleanor Vance</div>
          </div>
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Patient ID</div>
            <div className="font-mono font-bold text-slate-900">PAT-8801</div>
          </div>
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Age / Gender</div>
            <div className="font-bold text-slate-900">68 Yrs • Female</div>
          </div>
          <div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Communication Profile</div>
            <div className="font-bold text-slate-900">Verbal Patient</div>
          </div>
        </div>

        {/* Multimodal Assessment Summary Table */}
        <div>
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-200 pb-2 mb-3">
            1. Multimodal AI Score Summary
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200">
              <thead className="bg-slate-100 text-slate-700 font-bold uppercase text-[10px]">
                <tr>
                  <th className="p-2.5 border-b">Modality Channel</th>
                  <th className="p-2.5 border-b">Assessed Score</th>
                  <th className="p-2.5 border-b">Confidence</th>
                  <th className="p-2.5 border-b">Profile Weight</th>
                  <th className="p-2.5 border-b">Clinical Finding</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr>
                  <td className="p-2.5 font-semibold">Facial Expressive</td>
                  <td className="p-2.5 font-bold text-indigo-600">62 / 100</td>
                  <td className="p-2.5">94%</td>
                  <td className="p-2.5">35%</td>
                  <td className="p-2.5 text-slate-600">Elevated corrugator furrowing (AU4) & orbital narrowing</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-semibold">Physiological rPPG</td>
                  <td className="p-2.5 font-bold text-rose-600">70 / 100</td>
                  <td className="p-2.5">91%</td>
                  <td className="p-2.5">30%</td>
                  <td className="p-2.5 text-slate-600">Autonomic tachycardia (+14 BPM) & RMSSD suppression</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-semibold">Behavioral Posture</td>
                  <td className="p-2.5 font-bold text-purple-600">54 / 100</td>
                  <td className="p-2.5">88%</td>
                  <td className="p-2.5">20%</td>
                  <td className="p-2.5 text-slate-600">Moderate restlessness & protective guarding movement</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-semibold">Acoustic Voice</td>
                  <td className="p-2.5 font-bold text-teal-600">48 / 100</td>
                  <td className="p-2.5">86%</td>
                  <td className="p-2.5">15%</td>
                  <td className="p-2.5 text-slate-600">Vocalized sighing & pitch instability detected</td>
                </tr>
                <tr className="bg-slate-50 font-bold">
                  <td className="p-2.5 text-slate-900">Overall Composite Score</td>
                  <td className="p-2.5 text-rose-700 text-sm">68 / 100</td>
                  <td className="p-2.5 text-slate-900">89%</td>
                  <td className="p-2.5">100%</td>
                  <td className="p-2.5 text-rose-700 font-bold">High Pain-Distress Estimate</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Clinician Notes & Recommendations */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-200 pb-2">
            2. Attending Clinician Notes & Recommendations
          </h3>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-700 space-y-2">
            <p>
              <strong>Clinical Assessment:</strong> Patient Eleanor Vance exhibited acute incisional pain distress following day 2 post-operative hip replacement. Autonomic heart rate elevation was synchronized with facial Action Unit tightening.
            </p>
            <p>
              <strong>Intervention Administered:</strong> 5mg IV Morphine bolus administered at 08:25 AM. Post-intervention reassessment scheduled within 30 minutes.
            </p>
          </div>
        </div>

        {/* Regulatory Disclaimer & Signature */}
        <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="max-w-md">
            <p className="text-[11px] leading-relaxed">
              <strong>Regulatory Disclaimer:</strong> AI-assisted outputs are intended as assistive estimates for authorized clinical evaluation. They do not constitute a independent medical diagnosis.
            </p>
          </div>

          {/* Signature Line */}
          <div className="text-right">
            <div className="w-48 border-b border-slate-400 mb-1"></div>
            <div className="font-bold text-slate-900">Dr. Sarah Jenkins, MD</div>
            <div className="text-[10px] text-slate-400">Attending Physician Signature</div>
          </div>
        </div>
      </div>
    </div>
  );
};
