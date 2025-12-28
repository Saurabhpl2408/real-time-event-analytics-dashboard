import { BarChart3 } from 'lucide-react'

export default function EventTypeBreakdown({ eventsByType }) {
  const types = Object.entries(eventsByType || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10) // Top 10

  const maxCount = Math.max(...types.map(([, count]) => count), 1)

  if (types.length === 0) {
    return (
      <div className="glass-light dark:glass rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Event Types
          </h3>
          <BarChart3 className="w-5 h-5 text-gray-400" />
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
          No event data yet
        </p>
      </div>
    )
  }

  return (
    <div className="glass-light dark:glass rounded-xl border border-gray-200 dark:border-gray-800 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Top Event Types
        </h3>
        <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
      </div>
      
      <div className="space-y-3">
        {types.map(([eventType, count]) => {
          const percentage = (count / maxCount) * 100
          
          return (
            <div key={eventType}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                  {eventType.replace(/_/g, ' ')}
                </span>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {count.toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}