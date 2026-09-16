import axios from 'axios';

// ─── Axios Instance ───────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Response Interceptor ─────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timed out. Please try again.'));
    }
    if (!error.response) {
      return Promise.reject(
        new Error('Backend is currently unavailable. Please check the Render service.')
      );
    }
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      `Server error (${error.response.status})`;
    return Promise.reject(new Error(message));
  }
);

// ─── API Methods ──────────────────────────────────────────────────────────────

/** Check backend health */
export const healthCheck = () => api.get('/health');

/**
 * Get the latest ML result cached by the backend.
 * The simulator.py subprocess calls /fall/ml-process; the frontend
 * polls THIS endpoint instead so it never triggers the pipeline itself.
 * Returns HTTP 204 (no body) when no data has been processed yet.
 */
export const getLatestResult = () => api.get('/fall/latest');

/**
 * Full ML pipeline: activity recognition + fall detection + severity + notification
 * Only simulator.py should call this. Kept here for completeness/testing.
 * @param {Object} data - { sensor, inactivity_seconds, user_response }
 */
export const processFall = (data) => api.post('/fall/ml-process', data);

/**
 * ML-only fall detection (no side-effects)
 * @param {Object} sensor - SensorData object
 */
export const detectFall = (sensor) => api.post('/fall/ml-detect', sensor);

/**
 * Classify user activity from sensor data
 * @param {Object} data - { user_id, adxl_acc_x, ... itg_gyro_z }
 */
export const classifyActivity = (data) => api.post('/activity/classify', data);

/**
 * Fetch emergency notifications for a user
 * @param {string} userId
 */
export const getEmergencyNotifications = (userId) =>
  api.get(`/notifications/${userId}/emergency`);

/**
 * Acknowledge a notification
 * @param {number} notificationId
 */
export const acknowledgeNotification = (notificationId) =>
  api.patch(`/notifications/${notificationId}/acknowledge`);

/**
 * Resolve a notification
 * @param {number} notificationId
 */
export const resolveNotification = (notificationId) =>
  api.patch(`/notifications/${notificationId}/resolve`);

/**
 * Manually send an emergency notification
 * @param {Object} data - NotificationRequest body
 */
export const sendNotification = (data) => api.post('/notifications/send', data);

// ─── Simulator Control ────────────────────────────────────────────────────────

/** Start the simulator.py subprocess on the backend server */
export const simulatorStart = () => api.post('/simulator/start');

/** Stop the simulator.py subprocess on the backend server */
export const simulatorStop = () => api.post('/simulator/stop');

/** Get current simulator running status from the backend */
export const simulatorStatus = () => api.get('/simulator/status');

export default api;

