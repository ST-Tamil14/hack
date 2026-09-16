import { useState, useEffect, useRef, useCallback } from 'react';
import { getEmergencyNotifications, acknowledgeNotification, resolveNotification } from '../services/api';
import { useApp } from '../context/AppContext';

/**
 * Hook to fetch, cache, and manage emergency notifications for a user.
 */
export function useNotifications(intervalMs = 8000) {
  const { state, dispatch, addLog, showToast } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);

  const intervalRef = useRef(null);
  const isMounted = useRef(true);

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await getEmergencyNotifications(state.userId);
      if (!isMounted.current) return;
      const notifications = res.data?.notifications || [];
      dispatch({ type: 'SET_NOTIFICATIONS', payload: notifications });
      setError(null);
    } catch (err) {
      if (!isMounted.current) return;
      setError(err.message);
    } finally {
      if (isMounted.current) setLoading(false);
    }
  }, [state.userId, dispatch]);

  useEffect(() => {
    isMounted.current = true;
    fetchNotifications();
    intervalRef.current = setInterval(fetchNotifications, intervalMs);
    return () => {
      isMounted.current = false;
      clearInterval(intervalRef.current);
    };
  }, [state.userId]);

  const acknowledge = useCallback(async (notificationId) => {
    setActionLoading(notificationId);
    try {
      const res = await acknowledgeNotification(notificationId);
      const updated = res.data?.notification;
      if (updated) {
        dispatch({ type: 'UPDATE_NOTIFICATION', payload: updated });
      }
      addLog('Alert Acknowledged', `Notification #${notificationId} acknowledged`, 'success');
      showToast('Alert acknowledged successfully', 'success');
      await fetchNotifications();
    } catch (err) {
      showToast(`Failed to acknowledge: ${err.message}`, 'error');
      addLog('API Error', `Acknowledge failed: ${err.message}`, 'error');
    } finally {
      setActionLoading(null);
    }
  }, [dispatch, addLog, showToast, fetchNotifications]);

  const resolve = useCallback(async (notificationId) => {
    setActionLoading(notificationId);
    try {
      const res = await resolveNotification(notificationId);
      const updated = res.data?.notification;
      if (updated) {
        dispatch({ type: 'UPDATE_NOTIFICATION', payload: updated });
      }
      addLog('Alert Resolved', `Notification #${notificationId} resolved`, 'success');
      showToast('Alert resolved successfully', 'success');
      await fetchNotifications();
    } catch (err) {
      showToast(`Failed to resolve: ${err.message}`, 'error');
      addLog('API Error', `Resolve failed: ${err.message}`, 'error');
    } finally {
      setActionLoading(null);
    }
  }, [dispatch, addLog, showToast, fetchNotifications]);

  return {
    notifications: state.notifications,
    loading,
    error,
    actionLoading,
    refetch: fetchNotifications,
    acknowledge,
    resolve,
  };
}
