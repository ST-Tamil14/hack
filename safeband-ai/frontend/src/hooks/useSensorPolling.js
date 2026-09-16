import { useState, useEffect, useRef, useCallback } from 'react';
import { getLatestResult } from '../services/api';
import { useApp } from '../context/AppContext';

/**
 * Polls GET /fall/latest (read-only) every `intervalMs` ms.
 *
 * KEY ARCHITECTURE FIX:
 * The frontend MUST NOT trigger the ML pipeline (/fall/ml-process) on its own.
 * Only `simulator.py` (spawned via the Simulator page or run manually) posts readings
 * to /fall/ml-process. This hook simply polls /fall/latest for the cached output.
 *
 * - Returns 204 / empty when simulator has not posted any data yet.
 * - Returns 200 with JSON when simulator is actively running.
 * - Sets systemStatus to 'offline' when backend is unreachable.
 */
export function useSensorPolling(intervalMs = 2500) {
  const { dispatch, addLog } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [readingCount, setReadingCount] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isPolling, setIsPolling] = useState(false);

  const intervalRef = useRef(null);
  const isMounted = useRef(true);
  const readingRef = useRef(0);
  const lastTimestampRef = useRef(null);

  const fetchData = useCallback(async () => {
    if (!isMounted.current) return;

    try {
      const res = await getLatestResult();
      if (!isMounted.current) return;

      // HTTP 204 No Content -> No simulator run yet
      if (res.status === 204 || !res.data) {
        setData(null);
        setError(null);
        setLoading(false);
        dispatch({ type: 'SET_SYSTEM_STATUS', payload: 'online' });
        return;
      }

      const responseData = res.data;
      const ts = responseData.timestamp || JSON.stringify(responseData.sensor);

      // Only increment reading count if timestamp / payload actually changed
      if (ts !== lastTimestampRef.current) {
        lastTimestampRef.current = ts;
        readingRef.current += 1;
        setReadingCount(readingRef.current);
        addLog('Sensor Data', `Reading #${readingRef.current} received from backend`, 'success');
      }

      setData(responseData);
      setError(null);
      setLastUpdated(new Date().toISOString());
      dispatch({ type: 'SET_LAST_API_RESPONSE', payload: responseData });
      dispatch({ type: 'SET_SYSTEM_STATUS', payload: 'online' });
    } catch (err) {
      if (!isMounted.current) return;
      setError(err.message);
      dispatch({ type: 'SET_SYSTEM_STATUS', payload: 'offline' });
      addLog('API Error', err.message, 'error');
    } finally {
      if (isMounted.current) setLoading(false);
    }
  }, [dispatch, addLog]);

  const startPolling = useCallback(() => {
    if (intervalRef.current) return;
    setIsPolling(true);
    fetchData();
    intervalRef.current = setInterval(fetchData, intervalMs);
  }, [fetchData, intervalMs]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  useEffect(() => {
    isMounted.current = true;
    startPolling();
    return () => {
      isMounted.current = false;
      stopPolling();
    };
  }, [startPolling, stopPolling]);

  return {
    data,
    loading,
    error,
    readingCount,
    lastUpdated,
    isPolling,
    startPolling,
    stopPolling,
    refetch: fetchData,
  };
}
