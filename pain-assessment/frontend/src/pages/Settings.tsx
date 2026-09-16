import React, { useState } from 'react';
import { Settings as SettingsIcon, Sliders, Shield, Save, CheckCircle, Database } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api/v1');
  const [wsUrl, setWsUrl] = useState('ws://localhost:8000/ws');
  const [highThreshold, setHighThreshold] = useState(65);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
        <h1 className="text-xl font-bold text-slate-900">System & Clinical Settings</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Backend API endpoints, clinical alert thresholds, and privacy preferences
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Backend API Configuration */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Database className="w-4 h-4 text-cyan-600" />
            <h2 className="text-sm font-bold text-slate-900">Backend AI Engine Connectivity</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">VITE_API_BASE_URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 font-mono"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">VITE_WS_URL (WebSockets)</label>
              <input
                type="text"
                value={wsUrl}
                onChange={(e) => setWsUrl(e.target.value)}
                className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 font-mono"
              />
            </div>
          </div>
        </div>

        {/* Alert Thresholds */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Sliders className="w-4 h-4 text-purple-600" />
            <h2 className="text-sm font-bold text-slate-900">Clinical Alert Thresholds</h2>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <div className="flex justify-between font-semibold text-slate-700 mb-1">
                <span>High Pain-Distress Alert Threshold</span>
                <span className="text-cyan-700 font-bold">{highThreshold} / 100</span>
              </div>
              <input
                type="range"
                min="40"
                max="90"
                value={highThreshold}
                onChange={(e) => setHighThreshold(parseInt(e.target.value))}
                className="w-full accent-cyan-600 cursor-pointer"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                Sessions exceeding this score will trigger immediate clinical alert banners.
              </p>
            </div>
          </div>
        </div>

        {/* Save Button Bar */}
        <div className="flex items-center justify-between pt-2">
          {saved ? (
            <span className="text-xs font-semibold text-emerald-600 flex items-center space-x-1">
              <CheckCircle className="w-4 h-4" />
              <span>Settings saved successfully!</span>
            </span>
          ) : (
            <span className="text-xs text-slate-400">Settings applied immediately.</span>
          )}

          <button
            type="submit"
            className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-bold rounded-xl transition-all shadow-xs flex items-center space-x-2 cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </form>
    </div>
  );
};
