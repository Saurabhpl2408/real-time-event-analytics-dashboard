import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = {
  page_view: '#3b82f6',
  click: '#10b981',
  trade: '#f59e0b',
  purchase: '#8b5cf6',
  signup: '#ef4444'
}

function EventChart({ data }) {
  // Get all unique event types from the data
  const eventTypes = [...new Set(
    data.flatMap(item => 
      Object.keys(item).filter(key => key !== 'minute' && key !== 'total')
    )
  )]

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Events Over Time
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="minute" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Legend />
          {eventTypes.map(type => (
            <Line
              key={type}
              type="monotone"
              dataKey={type}
              stroke={COLORS[type] || '#6b7280'}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name={type.replace('_', ' ')}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default EventChart