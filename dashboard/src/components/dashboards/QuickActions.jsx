import { Download, Plus, Code, BarChart } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function QuickActions({ onExport }) {
  const navigate = useNavigate()

  const actions = [
    {
      label: 'New Schema',
      icon: Plus,
      color: 'from-blue-500 to-cyan-500',
      onClick: () => navigate('/schemas')
    },
    {
      label: 'New Adaptor',
      icon: Code,
      color: 'from-purple-500 to-pink-500',
      onClick: () => navigate('/adaptors')
    },
    {
      label: 'Export Data',
      icon: Download,
      color: 'from-green-500 to-emerald-500',
      onClick: onExport
    },
    {
      label: 'View Grafana',
      icon: BarChart,
      color: 'from-orange-500 to-red-500',
      onClick: () => window.open('http://localhost:3001', '_blank')
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {actions.map((action) => (
        <button
          key={action.label}
          onClick={action.onClick}
          className="glass-light dark:glass rounded-xl p-6 hover:shadow-lg transition-all group"
        >
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
            <action.icon className="w-6 h-6 text-white" />
          </div>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {action.label}
          </p>
        </button>
      ))}
    </div>
  )
}