import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = {
  page_view: '#667eea',
  click: '#10b981',
  purchase: '#f59e0b',
  signup: '#ef4444',
  trade: '#8b5cf6',
  custom: '#6366f1',
};

export default function EventChart({ eventsPerType }) {
  const chartData = Object.entries(eventsPerType || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    value: parseInt(value),
    color: COLORS[name] || '#6b7280',
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass rounded-lg p-3 border border-white/10">
          <p className="text-white font-medium">{payload[0].name}</p>
          <p className="text-gray-400 text-sm">
            {payload[0].value.toLocaleString()} events
          </p>
          <p className="text-gray-500 text-xs">
            {((payload[0].value / chartData.reduce((sum, item) => sum + item.value, 0)) * 100).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass rounded-2xl p-6 card-hover animate-fadeIn">
      <h3 className="text-xl font-bold text-white mb-4">Event Distribution</h3>
      
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[300px] flex items-center justify-center">
          <p className="text-gray-500">No event data available</p>
        </div>
      )}
      
      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 gap-2">
        {chartData.map((item, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-gray-400">{item.name}</span>
            <span className="text-sm text-white font-medium ml-auto">
              {item.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}