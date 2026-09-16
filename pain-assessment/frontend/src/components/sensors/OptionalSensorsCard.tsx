import React from 'react';
import { Cpu, Wifi, Activity, Heart, Thermometer } from 'lucide-react';
import { SensorDevice } from '../../types';

interface OptionalSensorsCardProps {
  sensors?: SensorDevice[];
}

export const OptionalSensorsCard: React.FC<OptionalSensorsCardProps> = ({ sensors }) => {
  const defaultSensors: SensorDevice[] = sensors || [
    {
      id: 'dev-1',
      name: 'WelchAllyn Digital BP Monitor',
      type: 'bp_monitor',
      status: 'connected',
      latest_reading: '120 / 80 mmHg',
      last_updated_at: '2 mins ago',
      battery_percent: 92,
    },
    {
      id: 'dev-2',
      name: 'Nonin Medical Pulse Oximeter',
      type: 'pulse_oximeter',
      status: 'connected',
      latest_reading: '98% SpO2 (PR: 76 BPM)',
      last_updated_at: 'Just now',
      battery_percent: 88,
    },
    {
      id: 'dev-3',
      name: 'iThermonitor Body Temp Patch',
      type: 'thermometer',
      status: 'connected',
      latest_reading: '36.8 °C',
      last_updated_at: '1 min ago',
      battery_percent: 75,
    },
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-slate-700" />
          <h3 className="text-sm font-bold text-slate-900">Reference Hardware Sensors</h3>
        </div>
        <span className="text-[10px] bg-slate-100 text-slate-600 font-semibold px-2 py-0.5 rounded-full">
          Hardware Monitored
        </span>
      </div>

      <div className="space-y-2">
        {defaultSensors.map((dev) => (
          <div
            key={dev.id}
            className="flex items-center justify-between bg-slate-50 p-2.5 rounded-lg border border-slate-200/60 text-xs"
          >
            <div>
              <div className="font-semibold text-slate-900">{dev.name}</div>
              <div className="text-[11px] text-slate-500">Reading: <span className="font-bold text-slate-800">{dev.latest_reading}</span></div>
            </div>

            <div className="text-right">
              <span className="inline-flex items-center space-x-1 text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md font-semibold text-[10px] border border-emerald-200">
                <Wifi className="w-3 h-3" />
                <span>Reference Validated</span>
              </span>
              <div className="text-[10px] text-slate-400 mt-0.5">{dev.last_updated_at}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
