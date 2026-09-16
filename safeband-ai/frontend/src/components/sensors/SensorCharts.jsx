import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg px-3 py-2 text-xs">
      <p className="text-slate-500 mb-1">Reading #{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }} className="font-medium">
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(3) : p.value}
        </p>
      ))}
    </div>
  );
};

function ChartCard({ title, data, lines, yLabel = '' }) {
  return (
    <div className="card p-4">
      <p className="text-sm font-semibold text-slate-700 mb-3">{title}</p>
      {data.length === 0 ? (
        <div className="h-40 flex items-center justify-center text-slate-400 text-xs">
          Waiting for data…
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={data} margin={{ top: 2, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="index" tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />
            {lines.map((l) => (
              <Line
                key={l.key}
                type="monotone"
                dataKey={l.key}
                name={l.name}
                stroke={l.color}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default function SensorCharts({ history }) {
  const accelData = history.map((h, i) => ({
    index: i + 1,
    'Acc X': h?.sensor?.adxl_acc_x ?? 0,
    'Acc Y': h?.sensor?.adxl_acc_y ?? 0,
    'Acc Z': h?.sensor?.adxl_acc_z ?? 0,
  }));

  const gyroData = history.map((h, i) => ({
    index: i + 1,
    'Gyro X': h?.sensor?.itg_gyro_x ?? 0,
    'Gyro Y': h?.sensor?.itg_gyro_y ?? 0,
    'Gyro Z': h?.sensor?.itg_gyro_z ?? 0,
  }));

  const heartData = history.map((h, i) => ({
    index: i + 1,
    'Heart Rate': h?.sensor?.heart_rate ?? 0,
  }));

  const spo2Data = history.map((h, i) => ({
    index: i + 1,
    'SpO2': h?.sensor?.spo2 ?? 0,
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ChartCard
        title="ADXL345 Accelerometer (m/s²)"
        data={accelData}
        lines={[
          { key: 'Acc X', name: 'X', color: '#0891b2' },
          { key: 'Acc Y', name: 'Y', color: '#7c3aed' },
          { key: 'Acc Z', name: 'Z', color: '#16a34a' },
        ]}
      />
      <ChartCard
        title="ITG3200 Gyroscope (°/s)"
        data={gyroData}
        lines={[
          { key: 'Gyro X', name: 'X', color: '#ea580c' },
          { key: 'Gyro Y', name: 'Y', color: '#db2777' },
          { key: 'Gyro Z', name: 'Z', color: '#2563eb' },
        ]}
      />
      <ChartCard
        title="Heart Rate (bpm)"
        data={heartData}
        lines={[{ key: 'Heart Rate', name: 'bpm', color: '#dc2626' }]}
      />
      <ChartCard
        title="SpO2 (%)"
        data={spo2Data}
        lines={[{ key: 'SpO2', name: 'SpO2 %', color: '#0891b2' }]}
      />
    </div>
  );
}
