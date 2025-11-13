import React, { useState, useEffect } from 'react';
import Header from './Header';
import MetricCard from './MetricCard';
import RealtimeChart from './RealtimeChart';
import EventChart from './EventChart';
import SessionsTable from './SessionsTable';
import { useWebSocket } from '../hooks/useWebSocket';
import { useStats } from '../hooks/useStats';
import apiService from '../services/api';

export default function Dashboard() {
  const { data: wsData, connected } = useWebSocket();
  const { stats, loading, error } = useStats(5000);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    // Fetch health status
    const fetchHealth = async () => {
      try {
        const healthData = await apiService.getHealth();
        setHealth(healthData);
      } catch (err) {
        console.error('Failed to fetch health:', err);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 10000); // Every 10 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <p className="text-red-400 font-medium mb-2">Failed to load dashboard</p>
          <p className="text-gray-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <Header health={health} connected={connected} />

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Events"
            value={stats.total_events}
            icon="📊"
            trend={12}
            color="blue"
            subtitle="All time"
          />
          <MetricCard
            title="Unique Sessions"
            value={stats.unique_sessions}
            icon="👥"
            trend={8}
            color="green"
            subtitle="Last 24 hours"
          />
          <MetricCard
            title="Unique Users"
            value={stats.unique_users}
            icon="🔥"
            trend={-3}
            color="yellow"
            subtitle="Last 24 hours"
          />
          <MetricCard
            title="Event Types"
            value={Object.keys(stats.events_per_type || {}).length}
            icon="🎯"
            color="purple"
            subtitle="Active"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <RealtimeChart 
            data={wsData} 
            title="Real-time Event Stream"
          />
          <EventChart 
            eventsPerType={stats.events_per_type}
          />
        </div>

        {/* Recent Activity Table */}
        <SessionsTable 
          recentAggregations={stats.recent_aggregations || []}
        />

        {/* Live Updates Indicator */}
        {connected && wsData && (
          <div className="fixed bottom-8 right-8 glass rounded-lg px-4 py-2 animate-slideInRight">
            <div className="flex items-center space-x-2">
              <div className="status-dot bg-green-500" />
              <span className="text-sm text-white">
                Live update: {wsData.event_type}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}