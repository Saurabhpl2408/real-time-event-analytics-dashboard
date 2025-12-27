import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import apiService from '@/services/api'
import { formatDistanceToNow } from 'date-fns'
import { Activity } from 'lucide-react'

export default function LiveEventFeed() {
  const token = useAuthStore((state) => state.token)

  const { data, isLoading } = useQuery({
    queryKey: ['recent-events'],
    queryFn: () => apiService.getRecentEvents(token, null, 20),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const getEventColor = (eventType) => {
    const colors = {
      'page_view': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      'github_project_click': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
      'linkedin_profile_click': 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
      'resume_download_click': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    }
    return colors[eventType] || 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
  }

  const formatEventType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  if (isLoading) {
    return (
      <div className="glass-light dark:glass rounded-xl p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const events = data?.events || []

  return (
    <div className="glass-light dark:glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Live Event Feed
          </h2>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs text-gray-500 dark:text-gray-400">Live</span>
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No events yet
          </div>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEventColor(event.event_type)}`}>
                    {formatEventType(event.event_type)}
                  </span>
                  {event.properties?.project_name && (
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      → {event.properties.project_name}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  {event.user_id?.substring(0, 8)} • {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}