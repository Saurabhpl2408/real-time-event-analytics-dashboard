import EventCounter from './EventCounter'
import EventChart from './EventChart'
import EventTypeDistribution from './EventTypeDistribution'

function Dashboard({ connected, totalEvents, eventsPerType, timeSeriesData }) {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          Real-Time Analytics Dashboard
        </h1>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <EventCounter 
          title="Total Events"
          count={totalEvents}
          icon="📊"
        />
        <EventCounter 
          title="Event Types"
          count={Object.keys(eventsPerType).length}
          icon="🏷️"
        />
        <EventCounter 
          title="Data Points"
          count={timeSeriesData.length}
          icon="📈"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Time Series Chart - Larger */}
        <div className="lg:col-span-2">
          <EventChart data={timeSeriesData} />
        </div>
        
        {/* Event Type Distribution */}
        <div className="lg:col-span-1">
          <EventTypeDistribution data={eventsPerType} />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Event Breakdown
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(eventsPerType).map(([type, count]) => (
            <div key={type} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-1 capitalize">
                {type.replace('_', ' ')}
              </div>
              <div className="text-2xl font-bold text-indigo-600">
                {count.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard