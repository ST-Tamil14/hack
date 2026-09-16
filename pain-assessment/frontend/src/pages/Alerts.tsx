import React, { useState, useEffect } from 'react';
import { Bell, AlertTriangle, CheckCircle, ShieldAlert, Filter, Search } from 'lucide-react';
import { api } from '../services/api';
import { ClinicalAlert } from '../types';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<ClinicalAlert[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    const data = await api.getAlerts();
    setAlerts(data);
  };

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id
          ? { ...a, acknowledged: true, acknowledged_by: 'Dr. Sarah Jenkins' }
          : a
      )
    );
  };

  const filteredAlerts = alerts.filter((a) => {
    if (severityFilter === 'all') return true;
    return a.severity === severityFilter;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Clinical Alerts & Notifications Center</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time threshold breaches, high pain-distress warnings, and signal quality flags
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="py-2 px-3 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-white"
          >
            <option value="all">All Severities</option>
            <option value="high">High & Critical</option>
            <option value="medium">Medium Severity</option>
            <option value="low">Low Severity</option>
          </select>
        </div>
      </div>

      {/* Alert Cards List */}
      <div className="space-y-3">
        {filteredAlerts.map((alert) => (
          <div
            key={alert.id}
            className={`bg-white p-4 rounded-2xl border shadow-2xs transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
              !alert.acknowledged ? 'border-amber-300 bg-amber-50/30' : 'border-slate-200'
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded-xl mt-0.5 border ${getSeverityBadge(alert.severity)}`}>
                <AlertTriangle className="w-5 h-5" />
              </div>

              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-sm font-bold text-slate-900">{alert.title}</h3>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border uppercase ${getSeverityBadge(alert.severity)}`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{alert.description}</p>
                <div className="text-[11px] text-slate-400">
                  Patient: <strong className="text-slate-700">{alert.patient_name}</strong> • Timestamp: {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
            </div>

            {/* Action / Acknowledged Status */}
            <div className="flex-shrink-0 text-right">
              {alert.acknowledged ? (
                <div className="text-xs text-emerald-600 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl font-semibold inline-flex items-center space-x-1.5">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  <span>Ack by {alert.acknowledged_by}</span>
                </div>
              ) : (
                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl transition-all shadow-xs cursor-pointer"
                >
                  Acknowledge Alert
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
