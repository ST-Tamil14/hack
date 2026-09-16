import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  Heart,
  Users,
  Video,
  AlertTriangle,
  FileText,
  ArrowUpRight,
  ShieldCheck,
  TrendingUp,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const Dashboard: React.FC = () => {
  const kpiData = [
    { label: 'Active Sessions', value: '2', sub: 'Live monitoring active', icon: Video, color: 'text-cyan-600 bg-cyan-50' },
    { label: 'Total Assessments', value: '148', sub: 'Past 30 days', icon: Activity, color: 'text-teal-600 bg-teal-50' },
    { label: 'Avg Pain-Distress', value: '42 / 100', sub: 'Moderate cohort avg', icon: TrendingUp, color: 'text-purple-600 bg-purple-50' },
    { label: 'Avg Heart Rate', value: '76 BPM', sub: 'Normal autonomic baseline', icon: Heart, color: 'text-rose-600 bg-rose-50' },
    { label: 'Signal Quality', value: '94%', sub: 'High rPPG SNR', icon: ShieldCheck, color: 'text-emerald-600 bg-emerald-50' },
    { label: 'Clinical Alerts', value: '1 Active', sub: 'Requires clinician review', icon: AlertTriangle, color: 'text-amber-600 bg-amber-50' },
  ];

  const trendChartData = [
    { time: '04:00', pain: 35, hr: 72 },
    { time: '06:00', pain: 42, hr: 75 },
    { time: '08:00', pain: 68, hr: 85 },
    { time: '10:00', pain: 54, hr: 80 },
    { time: '12:00', pain: 38, hr: 74 },
    { time: '14:00', pain: 45, hr: 77 },
  ];

  const recentSessions = [
    {
      id: 'sess-1001',
      patient: 'Eleanor Vance',
      patientId: 'PAT-8801',
      time: '08:15 - 08:30 AM',
      score: 68,
      level: 'High Pain',
      status: 'Needs Review',
      quality: '94%',
    },
    {
      id: 'sess-1002',
      patient: 'Marcus Brody',
      patientId: 'PAT-8802',
      time: '07:30 - 07:45 AM',
      score: 42,
      level: 'Moderate',
      status: 'Reviewed',
      quality: '89%',
    },
    {
      id: 'sess-1003',
      patient: 'Sophia Rodriguez',
      patientId: 'PAT-8803',
      time: 'Yesterday, 16:20',
      score: 28,
      level: 'Low',
      status: 'Reviewed',
      quality: '96%',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome & Quick Action Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Clinical Monitoring Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time multimodal pain distress estimates & physiological telemetry
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/patients"
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors flex items-center space-x-1.5"
          >
            <Users className="w-4 h-4" />
            <span>Patient Roster</span>
          </Link>
          <Link
            to="/assessment/new"
            className="px-4 py-2 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 rounded-xl transition-all shadow-xs flex items-center space-x-2"
          >
            <Video className="w-4 h-4" />
            <span>Start Live Assessment</span>
          </Link>
        </div>
      </div>

      {/* Summary KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
        {kpiData.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-500">{kpi.label}</span>
                <div className={`p-1.5 rounded-lg ${kpi.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="text-lg font-extrabold text-slate-900 leading-none">{kpi.value}</div>
              <div className="text-[10px] text-slate-400 font-medium">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Charts & Recent Sessions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Multimodal Trends Chart (2 Columns) */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Multimodal Pain & Heart Rate Trends</h2>
              <p className="text-xs text-slate-500">24-Hour continuous cohort telemetry</p>
            </div>
            <span className="text-xs font-semibold text-cyan-600 bg-cyan-50 px-2.5 py-1 rounded-lg border border-cyan-200">
              Live Aggregate
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPain" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorHr" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '10px' }} />
                <Area type="monotone" dataKey="pain" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#colorPain)" name="Pain Index (0-100)" />
                <Area type="monotone" dataKey="hr" stroke="#f43f5e" strokeWidth={2} fillOpacity={1} fill="url(#colorHr)" name="Heart Rate (BPM)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Active Status & Alerts Sidebar (1 Column) */}
        <div className="space-y-4">
          {/* Active Live Assessment Box */}
          <div className="bg-gradient-to-tr from-slate-900 to-slate-800 text-white p-5 rounded-2xl shadow-md space-y-3">
            <div className="flex items-center justify-between">
              <span className="flex items-center space-x-2 text-xs font-semibold text-emerald-400 bg-emerald-950/80 px-2.5 py-1 rounded-full border border-emerald-500/40">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Active Monitoring</span>
              </span>
              <Clock className="w-4 h-4 text-slate-400" />
            </div>

            <div>
              <div className="text-sm font-bold text-white">Eleanor Vance (PAT-8801)</div>
              <div className="text-xs text-slate-300">Room 402 • Post-Op Recovery</div>
            </div>

            <div className="bg-white/10 backdrop-blur-md p-3 rounded-xl flex items-center justify-between text-xs">
              <div>
                <div className="text-slate-300 text-[10px]">Current Pain Score</div>
                <div className="text-xl font-black text-white">68 / 100</div>
              </div>
              <div>
                <div className="text-slate-300 text-[10px]">rPPG Heart Rate</div>
                <div className="text-xl font-bold text-rose-400">82 BPM</div>
              </div>
            </div>

            <Link
              to="/assessment/new?patient_id=PAT-8801"
              className="w-full bg-cyan-500 hover:bg-cyan-600 text-white text-xs font-bold py-2.5 rounded-xl transition-all flex items-center justify-center space-x-1.5 shadow-sm"
            >
              <span>Jump to Live Stream</span>
              <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Quick Recent Alert */}
          <div className="bg-amber-50/80 border border-amber-200 p-4 rounded-2xl space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-amber-900">
              <div className="flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>High Distress Warning</span>
              </div>
              <span className="text-[10px] text-amber-700">08:22 AM</span>
            </div>
            <p className="text-xs text-amber-800 leading-relaxed">
              Patient Eleanor Vance reached 68/100 pain distress index with autonomic tachycardia (+14 BPM).
            </p>
            <Link to="/alerts" className="text-xs font-bold text-amber-900 underline block pt-1">
              Review Alert & Acknowledge →
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Patient Sessions Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Recent Patient Assessment Sessions</h2>
            <p className="text-xs text-slate-500">Historical clinician-reviewed multimodal assessments</p>
          </div>
          <Link to="/reports" className="text-xs font-semibold text-cyan-600 hover:text-cyan-800">
            View All Reports →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 font-semibold uppercase text-[10px]">
                <th className="pb-3">Patient</th>
                <th className="pb-3">Session ID</th>
                <th className="pb-3">Timestamp</th>
                <th className="pb-3">Pain Score</th>
                <th className="pb-3">Signal Quality</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentSessions.map((sess) => (
                <tr key={sess.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 font-semibold text-slate-900">
                    {sess.patient} <span className="text-slate-400 text-[11px] font-normal">({sess.patientId})</span>
                  </td>
                  <td className="py-3 text-slate-500 font-mono">{sess.id}</td>
                  <td className="py-3 text-slate-600">{sess.time}</td>
                  <td className="py-3">
                    <span
                      className={`font-bold px-2 py-0.5 rounded-md ${
                        sess.score > 60
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : sess.score > 35
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      }`}
                    >
                      {sess.score} / 100 ({sess.level})
                    </span>
                  </td>
                  <td className="py-3 font-semibold text-emerald-600">{sess.quality}</td>
                  <td className="py-3">
                    {sess.status === 'Needs Review' ? (
                      <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-md">
                        Needs Review
                      </span>
                    ) : (
                      <span className="bg-slate-100 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded-md flex items-center space-x-1 w-max">
                        <CheckCircle className="w-3 h-3 text-emerald-500" />
                        <span>Reviewed</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3 text-right">
                    <Link
                      to={`/reports?session_id=${sess.id}`}
                      className="text-cyan-600 hover:text-cyan-800 font-bold text-xs"
                    >
                      View Report
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
