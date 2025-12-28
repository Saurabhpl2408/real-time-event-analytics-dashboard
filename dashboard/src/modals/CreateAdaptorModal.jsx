import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import apiService from '@/services/api'

export default function CreateAdaptorModal({ onClose, onSuccess }) {
  const token = useAuthStore((state) => state.token)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    schema_id: '',
    website_url: '',
    description: '',
    allowed_domains: [],
  })

  // Fetch available schemas
  const { data: schemasData, isLoading: schemasLoading } = useQuery({
    queryKey: ['schemas'],
    queryFn: () => apiService.getSchemas(token),
  })

  const schemas = schemasData?.schemas || []

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Prepare data in the format backend expects
      const adaptorData = {
        name: formData.name,
        schema_id: formData.schema_id,
        website_url: formData.website_url,
        description: formData.description || undefined,
        allowed_domains: formData.allowed_domains.length > 0 
          ? formData.allowed_domains 
          : [formData.website_url.replace(/^https?:\/\//, '')],
        tracking_rules: {
          auto_page_view: true,
          track_clicks: true,
          track_forms: true
        },
        custom_code: null
      }

      console.log('Creating adaptor with data:', adaptorData)
      
      const response = await apiService.createAdaptor(adaptorData, token)
      
      console.log('Adaptor created:', response)
      onSuccess()
    } catch (error) {
      console.error('Adaptor creation error:', error)
      
      let errorMessage = 'Unknown error'
      if (error.message) {
        errorMessage = error.message
      } else if (typeof error === 'object') {
        errorMessage = JSON.stringify(error)
      } else {
        errorMessage = String(error)
      }
      
      alert('Failed to create adaptor: ' + errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-light dark:glass rounded-xl shadow-2xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Create New Adaptor
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Check if schemas exist */}
        {!schemasLoading && schemas.length === 0 && (
          <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <p className="text-sm text-yellow-800 dark:text-yellow-400">
              You need to create a schema first before creating an adaptor.
            </p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Adaptor Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., My Portfolio Tracker"
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Schema
            </label>
            <select
              name="schema_id"
              value={formData.schema_id}
              onChange={handleChange}
              required
              disabled={schemasLoading || schemas.length === 0}
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            >
              <option value="">Select a schema...</option>
              {schemas.map(schema => (
                <option key={schema.id} value={schema.name}>
                  {schema.name} - {schema.description || 'No description'}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              The schema defines what events this adaptor can track
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Website URL
            </label>
            <input
              type="text"
              name="website_url"
              value={formData.website_url}
              onChange={handleChange}
              required
              placeholder="e.g., http://localhost:8080 or https://example.com"
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Include the protocol (http:// or https://)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description (optional)
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              placeholder="Brief description of this adaptor..."
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || schemas.length === 0}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <span>Create Adaptor</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}