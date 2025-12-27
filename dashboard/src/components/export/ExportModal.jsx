import { useState } from 'react'
import { X, Download } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import apiService from '@/services/api'

export default function ExportModal({ isOpen, onClose, schemas }) {
  const [schemaId, setSchemaId] = useState('')
  const [eventType, setEventType] = useState('')
  const [days, setDays] = useState('7')
  const [format, setFormat] = useState('flattened')
  const [loading, setLoading] = useState(false)

  const token = useAuthStore((state) => state.token)

  const handleExport = async () => {
    if (!schemaId) return

    setLoading(true)
    try {
      let blob
      if (format === 'flattened') {
        blob = await apiService.exportCSVFlattened(token, schemaId, eventType || null, parseInt(days))
      } else {
        blob = await apiService.exportCSV(token, schemaId, eventType || null, parseInt(days))
      }

      // Download file
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${schemaId}_events_${Date.now()}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      onClose()
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="glass-light dark:glass rounded-2xl p-6 w-full max-w-md m-4 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Export to CSV</h2>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Schema
            </label>
            <select
              value={schemaId}
              onChange={(e) => setSchemaId(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="">Select schema...</option>
              {schemas?.map((schema) => (
                <option key={schema.id} value={schema.name}>
                  {schema.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Event Type (Optional)
            </label>
            <input
              type="text"
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              placeholder="Leave empty for all events"
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Time Range
            </label>
            <select
              value={days}
              onChange={(e) => setDays(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="1">Last 24 hours</option>
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Format
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  value="flattened"
                  checked={format === 'flattened'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Flattened (Recommended)</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  value="raw"
                  checked={format === 'raw'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Raw JSON</span>
              </label>
            </div>
          </div>

          <button
            onClick={handleExport}
            disabled={!schemaId || loading}
            className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <Download className="w-5 h-5" />
            <span>{loading ? 'Exporting...' : 'Export CSV'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}