import { Clock } from 'lucide-react'

export default function RecentEvents({ events }) {
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return 'just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  const getEventIcon = (eventType) => {
    const icons = {
      page_view: '👁️',
      click: '👆',
      form_submit: '📝',
      button_click: '🔘',
      github_project_click: '🔗',
      linkedin_profile_click: '💼',
      email_link_click: '📧',
      navigation_click: '🧭',
    }
    return icons[eventType] || '📊'
  }

  return (
    <div className="glass-light dark:glass rounded-xl border border-gray-200 dark:border-gray-800">
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Recent Events
        </h2>
      </div>
      
      <div className="divide-y divide-gray-200 dark:divide-gray-800 max-h-[600px] overflow-y-auto">
        {events.length === 0 ? (
          <div className="p-6 text-center text-gray-500 dark:text-gray-400">
            No events yet. Start tracking to see data here.
          </div>
        ) : (
          events.map((event, idx) => (
            <div key={idx} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div className="flex items-start space-x-3">
                <span className="text-2xl">{getEventIcon(event.event_type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                      {event.event_type.replace(/_/g, ' ')}
                    </p>
                    <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {formatTime(event.created_at || event.properties?.tracked_at)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {event.properties?.page_url || 'No URL'}
                  </p>
                  {event.properties?.link_text && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      "{event.properties.link_text}"
                    </p>
                  )}
                  {event.properties?.element_id && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      ID: {event.properties.element_id}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}