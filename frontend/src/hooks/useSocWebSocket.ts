import { useEffect, useRef, useState, useCallback } from 'react';
import {
  WsDetectionAlert,
  WsMetricsUpdate,
  WsTelemetryEnvelope,
  SimulationStatus,
  SecurityEvent,
} from '../types';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseSocWebSocketReturn {
  status: WebSocketStatus;
  latestAlert: WsDetectionAlert | null;
  alerts: WsDetectionAlert[];
  latestEvent: SecurityEvent | null;
  liveMetrics: WsMetricsUpdate | null;
  latestIncident: any | null;
  streamStatus: SimulationStatus | null;
  clearAlerts: () => void;
  send: (msg: any) => void;
}

export const useSocWebSocket = (urlOverride?: string): UseSocWebSocketReturn => {
  const [status, setStatus] = useState<WebSocketStatus>('connecting');
  const [latestAlert, setLatestAlert] = useState<WsDetectionAlert | null>(null);
  const [alerts, setAlerts] = useState<WsDetectionAlert[]>([]);
  const [latestEvent, setLatestEvent] = useState<SecurityEvent | null>(null);
  const [liveMetrics, setLiveMetrics] = useState<WsMetricsUpdate | null>(null);
  const [latestIncident, setLatestIncident] = useState<any | null>(null);
  const [streamStatus, setStreamStatus] = useState<SimulationStatus | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const pingIntervalRef = useRef<any>(null);
  const reconnectAttemptRef = useRef<number>(0);
  const isUnmountedRef = useRef<boolean>(false);

  const getWsUrl = useCallback(() => {
    if (urlOverride) return urlOverride;
    if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL;

    // Fallback: If dev port 5173, point to backend on 8000
    if (window.location.port === '5173' || window.location.hostname === 'localhost') {
      return 'ws://localhost:8000/ws/soc-telemetry';
    }
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/ws/soc-telemetry`;
  }, [urlOverride]);

  const connect = useCallback(() => {
    if (isUnmountedRef.current) return;

    try {
      const wsUrl = getWsUrl();
      setStatus('connecting');
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isUnmountedRef.current) return;
        setStatus('connected');
        reconnectAttemptRef.current = 0;

        // Start heartbeat ping
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: 'ping' }));
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        if (isUnmountedRef.current) return;
        try {
          const envelope: WsTelemetryEnvelope = JSON.parse(event.data);

          switch (envelope.type) {
            case 'DETECTION_ALERT': {
              const alert = envelope.data as WsDetectionAlert;
              setLatestAlert(alert);
              setAlerts((prev) => [alert, ...prev.slice(0, 9)]);
              break;
            }
            case 'EVENT_INGESTED': {
              setLatestEvent(envelope.data as SecurityEvent);
              break;
            }
            case 'METRICS_UPDATE': {
              setLiveMetrics(envelope.data as WsMetricsUpdate);
              break;
            }
            case 'INCIDENT_CREATED':
            case 'INCIDENT_UPDATED': {
              setLatestIncident(envelope.data);
              break;
            }
            case 'STREAM_STATUS': {
              setStreamStatus(envelope.data as SimulationStatus);
              break;
            }
            default:
              break;
          }
        } catch (err) {
          console.debug('Received non-JSON websocket message:', event.data);
        }
      };

      ws.onerror = () => {
        if (isUnmountedRef.current) return;
        setStatus('error');
      };

      ws.onclose = () => {
        if (isUnmountedRef.current) return;
        setStatus('disconnected');
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

        // Exponential backoff reconnect: 1s, 2s, 4s, max 10s
        const delay = Math.min(10000, 1000 * Math.pow(1.5, reconnectAttemptRef.current));
        reconnectAttemptRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      };
    } catch (err) {
      setStatus('error');
    }
  }, [getWsUrl]);

  useEffect(() => {
    isUnmountedRef.current = false;
    connect();

    return () => {
      isUnmountedRef.current = true;
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
    setLatestAlert(null);
  }, []);

  const send = useCallback((msg: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  }, []);

  return {
    status,
    latestAlert,
    alerts,
    latestEvent,
    liveMetrics,
    latestIncident,
    streamStatus,
    clearAlerts,
    send,
  };
};
