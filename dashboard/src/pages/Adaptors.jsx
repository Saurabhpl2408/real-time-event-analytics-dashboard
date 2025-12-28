import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from './../stores/authStore'
import apiService from './../services/api'
import AdaptorCard from './../components/adaptors/AdaptorCard'
import CreateAdaptorModal from './../modals/CreateAdaptorModal'
import { Plus } from 'lucide-react'

export default function Adaptors() {
  const token = useAuthStore((state) => state.token)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['adaptors'],
    queryFn: () => apiService.getAdaptors(token),
  })

  const handleDelete = async (containerId) => {
    if (!confirm('Delete this adaptor?')) return

    try {
      await apiService.deleteAdaptor(containerId, token)
      refetch()
    } catch (error) {
      alert('Failed to delete adaptor: ' + error.message)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-800 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-200 dark:bg-gray-800 rounded-xl animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  const adaptors = data?.adaptors || []

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Adaptors
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage tracking adaptors for your websites
          </p>
        </div>

        <button 
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl"
        >
          <Plus className="w-5 h-5" />
          <span>New Adaptor</span>
        </button>
      </div>

      {/* Adaptors grid */}
      {adaptors.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No adaptors yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {adaptors.map((adaptor) => (
            <AdaptorCard
              key={adaptor.id}
              adaptor={adaptor}
              onDelete={() => handleDelete(adaptor.container_id)}
              onEdit={() => alert('Edit coming soon')}
            />
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateAdaptorModal 
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            refetch()
          }}
        />
      )}
    </div>
  )
}