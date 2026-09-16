/**
 * Format a numeric sensor value to a fixed number of decimal places.
 * @param {number|null|undefined} value
 * @param {number} decimals
 * @param {string} unit
 * @returns {string}
 */
export function formatSensorValue(value, decimals = 2, unit = '') {
  if (value === null || value === undefined || isNaN(value)) return '—';
  const formatted = Number(value).toFixed(decimals);
  return unit ? `${formatted} ${unit}` : formatted;
}

/**
 * Format accelerometer value in m/s²
 */
export function formatAccel(value) {
  return formatSensorValue(value, 3, 'm/s²');
}

/**
 * Format gyroscope value in °/s
 */
export function formatGyro(value) {
  return formatSensorValue(value, 3, '°/s');
}

/**
 * Format heart rate in bpm
 */
export function formatHeartRate(value) {
  if (value === null || value === undefined) return '—';
  return `${Math.round(value)} bpm`;
}

/**
 * Format SpO2 as percentage
 */
export function formatSpO2(value) {
  if (value === null || value === undefined) return '—';
  return `${Math.round(value)}%`;
}

/**
 * Format confidence as percentage
 */
export function formatConfidence(value) {
  if (value === null || value === undefined) return '—';
  return `${(Number(value) * 100).toFixed(1)}%`;
}

/**
 * Format risk score as n/100
 */
export function formatRiskScore(value) {
  if (value === null || value === undefined) return '—';
  return `${Math.round(value)}/100`;
}
