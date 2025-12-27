import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from './../stores/authStore'
import { useNavigate } from 'react-router-dom'
import apiService from './../services/api'
import StatsCard from './../components/dashboards/StatsCard'
import LiveEventFeed from './../components/dashboards/LiveEventFeed'
import QuickActions from './../components/dashboards/QuickActions'
import ExportModal from './../components/export/ExportModal'
import { Activity, Database, Tags, TrendingUp } from 'lucide-react'
import { useState } from 'react'

export default function Dashboard() {
  const token = useAuthStore((state) => state.token)
  const navigate = useNavigate()
  const [exportModalOpen, setExportModalOpen] = useState(false)

  const { data: stats } = useQuery({
    queryKey: ['event-stats'],
    queryFn: () => apiService.getEventStats(token),
    refetchInterval: 5000,
  })

  const { data: schemasData } = useQuery({
    queryKey: ['schemas'],
    queryFn: () => apiService.getSchemas(token),
  })

  const { data: adaptorsData } = useQuery({
    queryKey: ['adaptors'],
    queryFn: () => apiService.getAdaptors(token),
  })

  return (
    <div className="space-y-8">
      
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Overview of your analytics platform
        </p>
      </div>

      {/* Stats cards - NOW CLICKABLE */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Events"
          value={stats?.total_events || 0}
          icon={Activity}
          color="blue"
          change={12}
          onClick={() => window.open('http://localhost:3001', '_blank')}
        />
        <StatsCard
          title="Schemas"
          value={schemasData?.total || 0}
          icon={Database}
          color="purple"
          onClick={() => navigate('/schemas')}
        />
        <StatsCard
          title="Adaptors"
          value={adaptorsData?.total || 0}
          icon={Tags}
          color="green"
          onClick={() => navigate('/adaptors')}
        />
        <StatsCard
          title="Recent Events"
          value={stats?.recent_events || 0}
          icon={TrendingUp}
          color="orange"
          onClick={() => window.open('http://localhost:3001', '_blank')}
        />
      </div>

      {/* Quick actions */}
      <QuickActions onExport={() => setExportModalOpen(true)} />

      {/* Live event feed */}
      <LiveEventFeed />

      {/* Export modal */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        schemas={schemasData?.schemas || []}
      />
    </div>
  )
}