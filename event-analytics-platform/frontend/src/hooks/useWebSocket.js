import { useEffect, useState, useRef } from 'react';
import apiService from '../services/api';

export const useWebSocket = () => {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    const handleMessage = (message) => {
      setData(message);
    };

    const handleError = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    // Connect to WebSocket
    wsRef.current = apiService.connectWebSocket(handleMessage, handleError);
    
    // Set connected state when connection opens
    wsRef.current.onopen = () => {
      setConnected(true);
    };

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { data, connected };
};