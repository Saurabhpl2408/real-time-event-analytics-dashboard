import { Code, ExternalLink, Copy, Trash2, Edit } from 'lucide-react'
import { useState } from 'react'

export default function AdaptorCard({ adaptor, onDelete, onEdit }) {
  const [copied, setCopied] = useState(false)

  const copyCode = () => {
    const code = `<script src="http://localhost:8000/tag/${adaptor.container_id}.js" async></script>`
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="glass-light dark:glass rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {adaptor.name}
            </h3>
            {adaptor.active ? (
              <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                Active
              </span>
            ) : (
              <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400">
                Inactive
              </span>
            )}
          </div>
          {adaptor.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {adaptor.description}
            </p>
          )}
          <div className="space-y-1 text-sm">
            <p className="text-gray-600 dark:text-gray-400">
              <span className="font-medium">Schema:</span> {adaptor.schema_id}
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              <span className="font-medium">Container ID:</span>{' '}
              <code className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-xs">
                {adaptor.container_id}
              </code>
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              <span className="font-medium">Events:</span> {adaptor.total_events?.count || 0}
            </p>
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

      {/* Installation code */}
      <div className="mt-4 p-3 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Code className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
              Installation Code
            </span>
          </div>
          <button
            onClick={copyCode}
            className="flex items-center space-x-1 px-2 py-1 rounded text-xs hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <Copy className="w-3 h-3" />
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>
        </div>
        <code className="text-xs text-gray-700 dark:text-gray-300 break-all">
          {`<script src="http://localhost:8000/tag/${adaptor.container_id}.js" async></script>`}
        </code>
      </div>

      {/* Website URL */}
      <div className="mt-3 flex items-center justify-between">
        <a>
          href={adaptor.website_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-1 text-sm text-blue-600 dark:text-blue-400 hover:underline" 
          <span>{adaptor.website_url}</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  )
}