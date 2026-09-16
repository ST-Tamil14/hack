import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Cpu, Heart, Zap, RefreshCw, Clock, Wifi, WifiOff, Play, Info } from 'lucide-react';
import SensorCard from '../components/sensors/SensorCard';
import SensorCharts from '../components/sensors/SensorCharts';
import LoadingState from '../components/ui/LoadingState';
import ErrorState from '../components/ui/ErrorState';
import { useSensorPolling } from '../hooks/useSensorPolling';
import { timeAgo } from '../utils/formatDate';

export default function LiveMonitoring() {
  const {
    data, loading, error,
    readingCount, lastUpdated, isPolling, refetch,
  } = useSensorPolling(2500);

  // ── Chart history (last 40 unique readings) ────────────────────────────────
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (data?.sensor) {
      setHistory((prev) => {
        const last = prev[prev.length - 1];
        if (
          last &&
          last.sensor.adxl_acc_x === data.sensor.adxl_acc_x &&
          last.sensor.adxl_acc_y === data.sensor.adxl_acc_y &&
          last.sensor.adxl_acc_z === data.sensor.adxl_acc_z &&
          last.sensor.heart_rate === data.sensor.heart_rate &&
          last.sensor.spo2 === data.sensor.spo2
        ) {
          return prev; // Skip duplicate reading
        }
        return [...prev, { sensor: data.sensor }].slice(-40);
      });
    }
  }, [data]);

  // Current sensor — use latest from data, fallback to last history entry
  const sensor = data?.sensor ?? history[history.length - 1]?.sensor ?? null;

  if (loading && history.length === 0) {
    return <LoadingState message="Connecting to live sensor stream…" />;
  }

  return (
    <div className="space-y-5 fade-in">

      {/* ── Status bar ─────────────────────────────────────────────────────── */}
      <div className="card p-3 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full flex-shrink-0
            ${isPolling && data ? 'bg-green-500 dot-blink' : 'bg-amber-400'}`}
          />
          <span className="text-xs font-medium text-slate-600">
            {!error && data ? 'Live Polling Active' : !error ? 'Waiting for Simulator Data' : 'Polling Error'}
          </span>
        </div>

        <div className="flex items-center gap-1 text-xs text-slate-400">
          <Cpu className="w-3.5 h-3.5" />
          <span>{readingCount} readings</span>
        </div>

        <div className="flex items-center gap-1 text-xs text-slate-400">
          <Clock className="w-3.5 h-3.5" />
          <span>Updated {timeAgo(lastUpdated)}</span>
        </div>

        <div className={`flex items-center gap-1 text-xs ml-auto font-medium
          ${!error ? 'text-brand-600' : 'text-red-500'}`}>
          {!error ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          <span>{!error ? 'Backend Connected' : 'Disconnected'}</span>
        </div>

        <button onClick={refetch} className="btn-secondary text-xs py-1.5">
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* ── Simulator Idle Banner (when no data yet) ──────────────────────── */}
      {!data && !error && (
        <div className="card p-4 bg-gradient-to-r from-brand-50 to-blue-50 border-brand-100 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-100 rounded-lg text-brand-700">
              <Info className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-brand-900">Simulator is Idle</p>
              <p className="text-xs text-brand-700">
                Start the simulator to stream live sensor readings and update real-time charts.
              </p>
            </div>
          </div>
          <Link to="/simulator" className="btn-primary text-xs px-3 py-2 flex items-center gap-1.5">
            <Play className="w-3.5 h-3.5 fill-current" />
            Go to Simulator
          </Link>
        </div>
      )}

      {/* ── Error banner ─────────────────────────────────────────────────── */}
      {error && (
        <div className="card">
          <ErrorState message={error} onRetry={refetch} />
        </div>
      )}

      {/* ── ADXL345 Accelerometer ────────────────────────────────────────── */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Cpu className="w-4 h-4 text-brand-600" />
          <p className="section-title">ADXL345 Accelerometer</p>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <SensorCard label="Acc X" value={sensor?.adxl_acc_x} unit="m/s²" color="brand" />
          <SensorCard label="Acc Y" value={sensor?.adxl_acc_y} unit="m/s²" color="brand" />
          <SensorCard label="Acc Z" value={sensor?.adxl_acc_z} unit="m/s²" color="brand" />
        </div>
      </div>

      {/* ── ITG3200 Gyroscope ────────────────────────────────────────────── */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-orange-500" />
          <p className="section-title">ITG3200 Gyroscope</p>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <SensorCard label="Gyro X" value={sensor?.itg_gyro_x} unit="°/s" color="orange" />
          <SensorCard label="Gyro Y" value={sensor?.itg_gyro_y} unit="°/s" color="orange" />
          <SensorCard label="Gyro Z" value={sensor?.itg_gyro_z} unit="°/s" color="orange" />
        </div>
      </div>

      {/* ── MMA8451Q Accelerometer ───────────────────────────────────────── */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Cpu className="w-4 h-4 text-purple-600" />
          <p className="section-title">MMA8451Q Accelerometer</p>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <SensorCard label="Acc X" value={sensor?.mma_acc_x} unit="m/s²" color="purple" />
          <SensorCard label="Acc Y" value={sensor?.mma_acc_y} unit="m/s²" color="purple" />
          <SensorCard label="Acc Z" value={sensor?.mma_acc_z} unit="m/s²" color="purple" />
        </div>
      </div>

      {/* ── Health readings ──────────────────────────────────────────────── */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Heart className="w-4 h-4 text-red-500" />
          <p className="section-title">Health-Awareness Readings</p>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          <SensorCard label="Heart Rate"  value={sensor?.heart_rate}  unit="bpm"   decimals={0} color="red"   />
          <SensorCard label="SpO2"        value={sensor?.spo2}        unit="%"     decimals={1} color="blue"  />
          <SensorCard label="Sugar Level" value={sensor?.sugar_level} unit="mg/dL" decimals={0} color="green" />
        </div>
      </div>

      {/* ── Live charts ──────────────────────────────────────────────────── */}
      <div>
        <p className="section-title mb-3">Live Sensor Charts</p>
        <SensorCharts history={history} />
      </div>
    </div>
  );
}
