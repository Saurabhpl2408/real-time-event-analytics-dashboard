import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import apiService from '@/services/api'
import SchemaCard from '@/components/schemas/SchemaCard'
import { Plus, AlertCircle } from 'lucide-react'

export default function Schemas() {
  const token = useAuthStore((state) => state.token)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['schemas'],
    queryFn: () => apiService.getSchemas(token),
  })

  const handleDelete = async (schemaName) => {
    if (!confirm(`Delete schema "${schemaName}"?`)) return

    try {
      await apiService.deleteSchema(schemaName, token)
      refetch()
    } catch (error) {
      alert('Failed to delete schema: ' + error.message)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-800 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-48 bg-gray-200 dark:bg-gray-800 rounded-xl animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  const schemas = data?.schemas || []

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Schemas
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Define event structures and properties
          </p>
        </div>

        <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl">
          <Plus className="w-5 h-5" />
          <span>New Schema</span>
        </button>
      </div>

      {/* Schema builder placeholder */}
      <div className="glass-light dark:glass rounded-xl p-8 border-2 border-dashed border-gray-300 dark:border-gray-700">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Schema Builder
          </h3>
          <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
            Visual schema builder coming soon. For now, use the API to create and manage schemas.
          </p>
        </div>
      </div>

      {/* Schemas grid */}
      {schemas.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No schemas yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemas.map((schema) => (
            <SchemaCard
              key={schema.id}
              schema={schema}
              onDelete={() => handleDelete(schema.name)}
              onEdit={() => alert('Edit coming soon')}
            />
          ))}
        </div>
      )}
    </div>
  )
}