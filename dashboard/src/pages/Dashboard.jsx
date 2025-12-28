import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import apiService from '../services/api'
import { Eye, MousePointerClick, FileText, Users } from 'lucide-react'

export default function Dashboard() {
  const token = useAuthStore((state) => state.token)

  const { data: stats, isLoading } = useQuery({
    queryKey: ['event-stats'],
    queryFn: () => apiService.getEventStats(token),
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

  const eventStats = stats?.stats || {}

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Real-time analytics overview
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Total Events
            </h3>
            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.total_events || 0).toLocaleString()}
          </p>
        </div>

        <div className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Page Views
            </h3>
            <Eye className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.page_views || 0).toLocaleString()}
          </p>
        </div>

        <div className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Clicks
            </h3>
            <MousePointerClick className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.clicks || 0).toLocaleString()}
          </p>
        </div>

        <div className="glass-light dark:glass rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Unique Sessions
            </h3>
            <Users className="w-5 h-5 text-orange-600 dark:text-orange-400" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(eventStats.unique_sessions || 0).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="glass-light dark:glass rounded-xl border border-gray-200 dark:border-gray-800 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Getting Started
        </h3>
        <ol className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
          <li className="flex items-start">
            <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">1.</span>
            <span>Create a schema for your events in the Schemas page</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">2.</span>
            <span>Set up an adaptor for your website in the Adaptors page</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">3.</span>
            <span>Install the tracking script on your website</span>
          </li>
          <li className="flex items-start">
            <span className="font-bold text-blue-600 dark:text-blue-400 mr-2">4.</span>
            <span>Watch real-time data flow in!</span>
          </li>
        </ol>
      </div>
    </div>
  )
}
