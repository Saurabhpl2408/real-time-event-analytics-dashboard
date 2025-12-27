import { Database, Trash2, Edit } from 'lucide-react'

export default function SchemaCard({ schema, onDelete, onEdit }) {
  const eventTypeCount = Object.keys(schema.properties || {}).length

  return (
    <div className="glass-light dark:glass rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {schema.name}
            </h3>
            {schema.description && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {schema.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={onEdit}
            className="p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-blue-600 dark:text-blue-400 transition-colors"
            title="Edit"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Event Types</span>
          <span className="font-medium text-gray-900 dark:text-white">{eventTypeCount}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Status</span>
          {schema.active ? (
            <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 text-xs font-medium">
              Active
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400 text-xs font-medium">
              Inactive
            </span>
          )}
        </div>
      </div>

      {/* Event types preview */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">Event Types:</p>
        <div className="flex flex-wrap gap-1">
          {Object.keys(schema.properties || {}).slice(0, 5).map((eventType) => (
            <span
              key={eventType}
              className="px-2 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
            >
              {eventType}
            </span>
          ))}
          {eventTypeCount > 5 && (
            <span className="px-2 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
              +{eventTypeCount - 5} more
            </span>
          )}
        </div>
      </div>
    </div>
  )
}