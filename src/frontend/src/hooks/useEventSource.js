import { useEffect, useRef, useState, useCallback } from 'react';

const BACKEND_URL = 'http://127.0.0.1:8000';

/**
 * useEventSource
 *
 * Opens a persistent SSE connection to the Flask /events/stream endpoint.
 * Automatically reconnects if the connection drops (with exponential back-off).
 *
 * Returns:
 *   events      — array of received event objects { type, data, timestamp }
 *   status      — 'connecting' | 'connected' | 'disconnected' | 'error'
 *   clearEvents — empties the events array
 *   emitEvent   — POST { type, data } to /events/emit  (fire-and-forget)
 *   runSim      — POST { solver } to /simulation/run
 *   backendOk   — boolean; true when /health responded 200
 */
export function useEventSource() {
  const [events, setEvents]     = useState([]);
  const [status, setStatus]     = useState('connecting');
  const [backendOk, setBackendOk] = useState(false);

  const esRef        = useRef(null);
  const retryTimer   = useRef(null);
  const retryCount   = useRef(0);
  const isMounted    = useRef(true);

  // ------------------------------------------------------------------
  // Health-check — runs once on mount and whenever the SSE reconnects
  // ------------------------------------------------------------------
  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/health`);
      if (isMounted.current) setBackendOk(res.ok);
    } catch {
      if (isMounted.current) setBackendOk(false);
    }
  }, []);

  // ------------------------------------------------------------------
  // Connect / reconnect
  // ------------------------------------------------------------------
  const connect = useCallback(() => {
    if (!isMounted.current) return;

    // Close any stale connection first
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }

    setStatus('connecting');
    checkHealth();

    const es = new EventSource(`${BACKEND_URL}/events/stream`);
    esRef.current = es;

    es.onopen = () => {
      if (!isMounted.current) return;
      retryCount.current = 0;
      setStatus('connected');
    };

    es.onmessage = (e) => {
      if (!isMounted.current) return;
      try {
        const event = JSON.parse(e.data);
        setEvents(prev => [...prev, event]);
      } catch {
        // malformed frame — ignore
      }
    };

    es.onerror = () => {
      if (!isMounted.current) return;
      es.close();
      esRef.current = null;
      setStatus('error');
      setBackendOk(false);

      // Exponential back-off: 1 s, 2 s, 4 s … capped at 30 s
      const delay = Math.min(1000 * 2 ** retryCount.current, 30_000);
      retryCount.current += 1;
      retryTimer.current = setTimeout(connect, delay);
    };
  }, [checkHealth]);

  // ------------------------------------------------------------------
  // Mount / unmount lifecycle
  // ------------------------------------------------------------------
  useEffect(() => {
    isMounted.current = true;
    connect();

    return () => {
      isMounted.current = false;
      clearTimeout(retryTimer.current);
      if (esRef.current) {
        esRef.current.close();
        esRef.current = null;
      }
    };
  }, [connect]);

  // ------------------------------------------------------------------
  // Public actions
  // ------------------------------------------------------------------
  const emitEvent = useCallback(async (type, data = {}) => {
    try {
      await fetch(`${BACKEND_URL}/events/emit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, data }),
      });
    } catch {
      // backend unreachable — silently ignore; UI already shows disconnected
    }
  }, []);

  const runSim = useCallback(async (solver = 'classical') => {
    try {
      const res = await fetch(`${BACKEND_URL}/simulation/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ solver }),
      });
      return res.ok;
    } catch {
      return false;
    }
  }, []);

  const clearEvents = useCallback(() => setEvents([]), []);

  return { events, status, backendOk, clearEvents, emitEvent, runSim };
}
