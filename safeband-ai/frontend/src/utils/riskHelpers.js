/**
 * Get Tailwind color classes for a severity level.
 * @param {'low'|'medium'|'high'|'critical'} severity
 */
export function getSeverityColors(severity) {
  const s = (severity || '').toLowerCase();
  switch (s) {
    case 'critical':
      return {
        bg: 'bg-red-50',
        border: 'border-red-200',
        badge: 'bg-red-100 text-red-700 border-red-200',
        text: 'text-red-700',
        bar: 'bg-red-500',
        dot: 'bg-red-500',
      };
    case 'high':
      return {
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        badge: 'bg-orange-100 text-orange-700 border-orange-200',
        text: 'text-orange-700',
        bar: 'bg-orange-500',
        dot: 'bg-orange-500',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        badge: 'bg-yellow-100 text-yellow-700 border-yellow-200',
        text: 'text-yellow-700',
        bar: 'bg-yellow-500',
        dot: 'bg-yellow-400',
      };
    case 'low':
    default:
      return {
        bg: 'bg-green-50',
        border: 'border-green-200',
        badge: 'bg-green-100 text-green-700 border-green-200',
        text: 'text-green-700',
        bar: 'bg-green-500',
        dot: 'bg-green-500',
      };
  }
}

/**
 * Get Tailwind color classes for a notification/alert status.
 */
export function getStatusColors(status) {
  const s = (status || '').toLowerCase();
  switch (s) {
    case 'sent':
      return 'bg-blue-100 text-blue-700 border-blue-200';
    case 'acknowledged':
      return 'bg-cyan-100 text-cyan-700 border-cyan-200';
    case 'resolved':
      return 'bg-green-100 text-green-700 border-green-200';
    case 'failed':
      return 'bg-red-100 text-red-700 border-red-200';
    case 'simulated':
    default:
      return 'bg-slate-100 text-slate-600 border-slate-200';
  }
}

/**
 * Get label for a fall detection status.
 */
export function getFallStatusLabel(mlResult, confirmation) {
  if (!mlResult) return 'Normal';
  if (mlResult.model_detected_fall && confirmation?.confirmed) return 'Confirmed Fall';
  if (mlResult.model_detected_fall) return 'Possible Fall';
  return 'Normal';
}

/**
 * Get Tailwind color classes for a fall status.
 */
export function getFallStatusColors(status) {
  switch (status) {
    case 'Confirmed Fall':
    case 'Emergency Alert Sent':
      return {
        bg: 'bg-red-50',
        badge: 'bg-red-100 text-red-700 border-red-200',
        text: 'text-red-700',
      };
    case 'Possible Fall':
      return {
        bg: 'bg-orange-50',
        badge: 'bg-orange-100 text-orange-700 border-orange-200',
        text: 'text-orange-700',
      };
    default:
      return {
        bg: 'bg-green-50',
        badge: 'bg-green-100 text-green-700 border-green-200',
        text: 'text-green-700',
      };
  }
}

/**
 * Map activity name to a simple emoji/icon key.
 */
export function getActivityIcon(activity) {
  const a = (activity || '').toLowerCase();
  if (a.includes('walk')) return 'walking';
  if (a.includes('run')) return 'running';
  if (a.includes('sit')) return 'sitting';
  if (a.includes('stand')) return 'standing';
  if (a.includes('lie') || a.includes('lying')) return 'lying';
  if (a.includes('fall')) return 'falling';
  return 'unknown';
}

/**
 * Check if a risk score warrants an emergency level.
 */
export function isEmergencyRisk(riskScore) {
  return riskScore >= 70;
}

/**
 * Get the display label for a risk score range.
 */
export function getRiskLabel(riskScore) {
  if (riskScore >= 75) return 'Critical';
  if (riskScore >= 50) return 'High';
  if (riskScore >= 25) return 'Medium';
  return 'Low';
}
