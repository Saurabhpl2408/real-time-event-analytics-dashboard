import React, { useEffect, useState } from 'react';

export default function MetricCard({ 
  title, 
  value, 
  icon, 
  trend, 
  color = 'blue',
  subtitle 
}) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    // Animate number counting
    let start = 0;
    const end = parseInt(value) || 0;
    const duration = 1000; // 1 second
    const increment = end / (duration / 16); // 60fps

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setDisplayValue(end);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value]);

  const colorClasses = {
    blue: 'from-blue-500/20 to-purple-500/20 border-blue-500/30',
    green: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    yellow: 'from-yellow-500/20 to-orange-500/20 border-yellow-500/30',
    red: 'from-red-500/20 to-pink-500/20 border-red-500/30',
    purple: 'from-purple-500/20 to-indigo-500/20 border-purple-500/30',
  };

  const iconColorClasses = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  };

  return (
    <div className={`
      glass rounded-2xl p-6 card-hover
      bg-gradient-to-br ${colorClasses[color]}
      animate-fadeIn
    `}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
          <h3 className="text-4xl font-bold text-white animate-countUp">
            {displayValue.toLocaleString()}
          </h3>
          {subtitle && (
            <p className="text-gray-500 text-xs mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`
          text-4xl ${iconColorClasses[color]}
          transform transition-transform hover:scale-110
        `}>
          {icon}
        </div>
      </div>
      
      {trend && (
        <div className="flex items-center space-x-2">
          <span className={`
            text-sm font-medium
            ${trend > 0 ? 'text-green-400' : 'text-red-400'}
          `}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
          <span className="text-gray-500 text-xs">vs last hour</span>
        </div>
      )}
    </div>
  );
}