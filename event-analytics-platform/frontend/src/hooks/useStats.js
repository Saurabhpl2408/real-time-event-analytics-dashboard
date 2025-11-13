import { useState, useEffect } from 'react';
import apiService from '../services/api';

export const useStats = (refreshInterval = 5000) => {
  const [stats, setStats] = useState({
    total_events: 0,
    events_per_type: {},
    recent_aggregations: [],
    unique_sessions: 0,
    unique_users: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      const data = await apiService.getStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    // Set up periodic refresh
    const interval = setInterval(fetchStats, refreshInterval);
    
    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { stats, loading, error, refetch: fetchStats };
};