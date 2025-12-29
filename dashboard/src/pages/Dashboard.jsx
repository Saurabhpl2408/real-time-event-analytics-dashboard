import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import apiService from '../services/api'
import { Eye, MousePointerClick, FileText, Users, ExternalLink, TrendingUp } from 'lucide-react'

function getEventIcon(eventType) {
  const iconMap = {
    'page_view': Eye,
    'github_project_click': FileText,
    'github_profile_click': FileText,
    'linkedin_profile_click': Users,
    'email_link_click': FileText,
    'contact_number_click': FileText,
    'navigation_click': MousePointerClick,
    'external_link_click': ExternalLink,
    'resume_download_click': FileText,
    'get_in_touch_click': MousePointerClick,
  }
  return iconMap[eventType] || MousePointerClick
}

function formatEventTypeName(eventType) {
  return eventType.replace(/_/g, ' ').replace(/click$/, '').trim()
}

export default function Dashboard() {
  const token = useAuthStore((state) => state.token)

  const { data: stats, isLoading } = useQuery({
    queryKey: ['event-stats'],
    queryFn: () => apiService.getEventStats(token, null, 7),
    refetchInterval: 5000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    )
  }

  const eventStats = stats || {}
  const grafanaUrl = 'http://localhost:3001'

  const handleCardClick = (cardType) => {
    window.open(grafanaUrl, '_blank')
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Real-time analytics overview</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <button
          onClick={() => handleCardClick('events')}
          className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800 hover:shadow-xl hover:scale-105 transition-all cursor-pointer text-left group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Events</h3>
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:scale-110 transition-transform">
              <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.total_events || 0).toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center">
            <ExternalLink className="w-3 h-3 mr-1" />
            Click to view in Grafana
          </p>
        </button>

        <button
          onClick={() => handleCardClick('pageviews')}
          className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800 hover:shadow-xl hover:scale-105 transition-all cursor-pointer text-left group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Page Views</h3>
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg group-hover:scale-110 transition-transform">
              <Eye className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.page_views || 0).toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center">
            <ExternalLink className="w-3 h-3 mr-1" />
            Click to view in Grafana
          </p>
        </button>

        <button
          onClick={() => handleCardClick('clicks')}
          className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800 hover:shadow-xl hover:scale-105 transition-all cursor-pointer text-left group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Clicks</h3>
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg group-hover:scale-110 transition-transform">
              <MousePointerClick className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.clicks || 0).toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center">
            <ExternalLink className="w-3 h-3 mr-1" />
            Click to view in Grafana
          </p>
        </button>

        <button
          onClick={() => handleCardClick('sessions')}
          className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800 hover:shadow-xl hover:scale-105 transition-all cursor-pointer text-left group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Unique Sessions</h3>
            <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg group-hover:scale-110 transition-transform">
              <Users className="w-5 h-5 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.unique_sessions || 0).toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center">
            <ExternalLink className="w-3 h-3 mr-1" />
            Click to view in Grafana
          </p>
        </button>
      </div>

      {eventStats.events_by_type && Object.keys(eventStats.events_by_type).length > 0 && (
        <div className="glass-light dark:glass rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Events by Type</h3>
            <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(eventStats.events_by_type).sort((a, b) => b[1] - a[1]).map(([type, count]) => {
              const Icon = getEventIcon(type)
              const percentage = ((count / eventStats.total_events) * 100).toFixed(1)
              return (
                <div key={type} className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <Icon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white capitalize truncate">
                        {formatEventTypeName(type)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{percentage}% of total</p>
                    </div>
                    <span className="text-lg font-bold text-gray-900 dark:text-white">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div
                      className="bg-gradient-to-r from-blue-600 to-cyan-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="glass-light dark:glass rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Getting Started</h3>
        <ol className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
          <li className="flex items-start">
            <span className="font-bold text-green-600 dark:text-green-400 mr-2">✓</span>
            <span>Schema created for portfolio events</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-green-600 dark:text-green-400 mr-2">✓</span>
            <span>Adaptor set up for website tracking</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">3.</span>
            <span>Install the tracking script on your portfolio website</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">4.</span>
            <span>View detailed analytics in Grafana dashboards 📊</span>
          </li>
        </ol>
      </div>
    </div>
  )
}
