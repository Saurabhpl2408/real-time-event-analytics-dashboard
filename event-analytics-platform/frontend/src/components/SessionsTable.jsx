import React from 'react';

export default function SessionsTable({ recentAggregations }) {
  // Transform aggregations data for display
  const tableData = recentAggregations.slice(0, 10).map((agg, index) => ({
    id: index,
    time: Object.keys(agg)[0] || 'N/A',
    events: Object.values(agg).reduce((sum, val) => sum + parseInt(val || 0), 0),
    types: Object.keys(agg).length,
  }));

  return (
    <div className="glass rounded-2xl p-6 card-hover animate-fadeIn">
      <h3 className="text-xl font-bold text-white mb-4">Recent Activity</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">
                Time Window
              </th>
              <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">
                Total Events
              </th>
              <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">
                Event Types
              </th>
              <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {tableData.length > 0 ? (
              tableData.map((row, index) => (
                <tr 
                  key={row.id}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <td className="py-3 px-4 text-white font-mono text-sm">
                    {row.time}
                  </td>
                  <td className="py-3 px-4 text-white font-medium">
                    {row.events.toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-gray-400">
                    {row.types} types
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                      Processed
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="py-8 text-center text-gray-500">
                  No recent activity
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}