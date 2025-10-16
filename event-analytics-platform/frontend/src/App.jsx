import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'

function App() {
  const [connected, setConnected] = useState(false)
  const [ws, setWs] = useState(null)
  const [data, setData] = useState({
    totalEvents: 0,
    eventsPerType: {},
    timeSeriesData: []
  })

  useEffect(() => {
    // Determine WebSocket URL based on environment
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.hostname
    const wsPort = window.location.port ? `:${window.location.port}` : ''
    const wsUrl = `${wsProtocol}//${wsHost}${wsPort}/ws`
    
    console.log('Connecting to WebSocket:', wsUrl)
    
    const websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
    }
    
    websocket.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data)
        
        setData(prevData => {
          // Update time series data
          const newTimeSeriesData = [...prevData.timeSeriesData]
          
          // Find if this minute already exists
          const existingIndex = newTimeSeriesData.findIndex(
            item => item.minute === update.minute
          )
          
          if (existingIndex >= 0) {
            // Update existing entry
            newTimeSeriesData[existingIndex] = {
              ...newTimeSeriesData[existingIndex],
              [update.event_type]: update.count,
              total: Object.values(update.events_per_type).reduce((a, b) => a + b, 0)
            }
          } else {
            // Add new entry
            newTimeSeriesData.push({
              minute: update.minute,
              [update.event_type]: update.count,
              total: update.total_events
            })
          }
          
          // Keep only last 20 minutes
          const sortedData = newTimeSeriesData
            .sort((a, b) => a.minute.localeCompare(b.minute))
            .slice(-20)
          
          return {
            totalEvents: update.total_events,
            eventsPerType: update.events_per_type,
            timeSeriesData: sortedData
          }
        })
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnected(false)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)
    }
    
    setWs(websocket)
    
    return () => {
      if (websocket) {
        websocket.close()
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Dashboard 
        connected={connected}
        totalEvents={data.totalEvents}
        eventsPerType={data.eventsPerType}
        timeSeriesData={data.timeSeriesData}
      />
    </div>
  )
}

export default App