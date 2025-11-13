import React from 'react';

export default function Header({ health, connected }) {
  return (
    <header className="glass rounded-2xl p-6 mb-8 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">
            InsightFlow Analytics
          </h1>
          <p className="text-gray-400">
            Real-time event analytics with ML-powered insights
          </p>
        </div>
        
        <div className="flex items-center space-x-6">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`status-dot ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-400">
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Health Status */}
          {health && (
            <div className="flex items-center space-x-4">
              <StatusBadge label="Kafka" status={health.kafka} />
              <StatusBadge label="Redis" status={health.redis} />
              <StatusBadge label="Database" status={health.database} />
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function StatusBadge({ label, status }) {
  const isConnected = status === 'connected';
  
  return (
    <div className={`
      px-3 py-1 rounded-full text-xs font-medium
      ${isConnected 
        ? 'bg-green-500/20 text-green-400' 
        : 'bg-red-500/20 text-red-400'
      }
    `}>
      {label}: {status}
    </div>
  );
}