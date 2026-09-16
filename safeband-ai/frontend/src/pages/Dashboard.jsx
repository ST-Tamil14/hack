import { useState, useEffect, useRef } from 'react';
import {
  Wifi, WifiOff, Activity, Shield, AlertTriangle, Bell,
  CheckCircle, RefreshCw, Cpu, Clock, Play, Square
} from 'lucide-react';
import StatCard from '../components/ui/StatCard';
import FallDetectionCard from '../components/fall/FallDetectionCard';
import SeverityCard from '../components/fall/SeverityCard';
import ActivityCard from '../components/activity/ActivityCard';
import LocationCard from '../components/location/LocationCard';
import FallConfirmModal from '../components/fall/FallConfirmModal';
import EmergencyBanner from '../components/alerts/EmergencyBanner';
import ErrorState from '../components/ui/ErrorState';
import { useSensorPolling } from '../hooks/useSensorPolling';
import { useNotifications } from '../hooks/useNotifications';
import { useApp } from '../context/AppContext';
import { formatConfidence } from '../utils/formatSensorValue';
import { timeAgo } from '../utils/formatDate';

export default function Dashboard() {
  const { state } = useApp();
  const { data, loading, error, readingCount, lastUpdated, refetch } = useSensorPolling(4000);
  const { notifications } = useNotifications(8000);
  const [activityHistory, setActivityHistory] = useState([]);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmHandled, setConfirmHandled] = useState(false);
  const prevFallRef = useRef(false);

  // Track activity history
  useEffect(() => {
    if (data?.activity) {
      setActivityHistory((h) => [...h, { activity: data.activity.activity || data.activity.classified_activity }].slice(-10));
    }
  }, [data]);

  // Trigger fall confirm modal on new fall detection
  useEffect(() => {
    const fallNow = data?.ml_detection?.model_detected_fall;
    if (fallNow && !prevFallRef.current && !confirmHandled) {
      setShowConfirmModal(true);
    }
    if (!fallNow) {
      setConfirmHandled(false);
    }
    prevFallRef.current = fallNow || false;
  }, [data?.ml_detection?.model_detected_fall]);

  const activeAlerts = notifications.filter(
    (n) => n.status !== 'resolved' && n.status !== 'acknowledged'
  );
  const acknowledgedAlerts = notifications.filter((n) => n.status === 'acknowledged');
  const resolvedAlerts = notifications.filter((n) => n.status === 'resolved');

  const mlDetection = data?.ml_detection;
  const fallDetected = mlDetection?.model_detected_fall;
  const confirmed = data?.confirmation?.confirmed;
  const activity = data?.activity?.activity || data?.activity?.classified_activity || '—';
  const severity = data?.severity;
  const riskScore = severity?.risk_score ?? 0;

  let riskLabel = 'Low';
  if (riskScore >= 75) riskLabel = 'Critical';
  else if (riskScore >= 50) riskLabel = 'High';
  else if (riskScore >= 25) riskLabel = 'Medium';

  return (
    <div className="space-y-5 fade-in">
      {/* Emergency banner */}
      {activeAlerts.length > 0 && <EmergencyBanner count={activeAlerts.length} />}

      {/* Top stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
        <StatCard
          title="System Status"
          value={state.systemStatus === 'online' ? 'Online' : state.systemStatus === 'offline' ? 'Offline' : 'Checking…'}
          subtitle={`${readingCount} readings received`}
          icon={state.systemStatus === 'online' ? Wifi : WifiOff}
          iconBg={state.systemStatus === 'online' ? 'bg-green-50' : 'bg-red-50'}
          iconColor={state.systemStatus === 'online' ? 'text-green-600' : 'text-red-600'}
          loading={loading}
        />
        <StatCard
          title="Current Activity"
          value={activity}
          subtitle={`Confidence: ${formatConfidence(mlDetection?.confidence)}`}
          icon={Activity}
          iconBg="bg-brand-50"
          iconColor="text-brand-600"
          loading={loading}
        />
        <StatCard
          title="Fall Detection"
          value={fallDetected ? (confirmed ? 'Confirmed Fall' : 'Possible Fall') : 'No Fall'}
          subtitle={`Confidence: ${formatConfidence(mlDetection?.confidence)}`}
          icon={AlertTriangle}
          alert={!!fallDetected}
          iconBg={fallDetected ? 'bg-red-50' : 'bg-green-50'}
          iconColor={fallDetected ? 'text-red-600' : 'text-green-600'}
          loading={loading}
        />
        <StatCard
          title="Risk Level"
          value={riskLabel}
          subtitle={`Score: ${Math.round(riskScore)}/100`}
          icon={Shield}
          iconBg={riskScore >= 50 ? 'bg-red-50' : riskScore >= 25 ? 'bg-orange-50' : 'bg-green-50'}
          iconColor={riskScore >= 50 ? 'text-red-600' : riskScore >= 25 ? 'text-orange-600' : 'text-green-600'}
          loading={loading}
        />
        <StatCard
          title="Active Alerts"
          value={activeAlerts.length}
          subtitle={`${acknowledgedAlerts.length} ack · ${resolvedAlerts.length} resolved`}
          icon={Bell}
          alert={activeAlerts.length > 0}
          iconBg="bg-blue-50"
          iconColor="text-blue-600"
          loading={loading}
        />
      </div>

      {/* Error state */}
      {error && !loading && (
        <div className="card">
          <ErrorState message={error} onRetry={refetch} />
        </div>
      )}

      {/* Main grid */}
      {!error && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left column */}
          <div className="lg:col-span-2 space-y-4">
            <ActivityCard activityResult={data?.activity} history={activityHistory} />
            <FallDetectionCard
              mlDetection={mlDetection}
              confirmation={data?.confirmation}
              lastUpdated={lastUpdated}
            />
          </div>

          {/* Right column */}
          <div className="space-y-4">
            <SeverityCard severity={severity} />
            <LocationCard sensor={data?.sensor} lastUpdated={lastUpdated} />

            {/* Last update info */}
            <div className="card p-4">
              <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide">
                System Info
              </p>
              <div className="space-y-2 text-xs text-slate-600">
                <div className="flex justify-between">
                  <span className="text-slate-400">User ID</span>
                  <span className="font-mono font-medium">{state.userId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Readings</span>
                  <span className="font-medium">{readingCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Last Update</span>
                  <span className="font-medium">{timeAgo(lastUpdated)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Data Source</span>
                  <span className="font-medium text-brand-600">Backend Simulator</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Fall confirmation modal */}
      {showConfirmModal && (
        <FallConfirmModal
          detectedAt={lastUpdated}
          onSafe={() => { setShowConfirmModal(false); setConfirmHandled(true); }}
          onConfirm={() => { setShowConfirmModal(false); setConfirmHandled(true); }}
          onUnableToRespond={() => { setShowConfirmModal(false); setConfirmHandled(true); }}
          onDismiss={() => { setShowConfirmModal(false); setConfirmHandled(true); }}
        />
      )}
    </div>
  );
}
