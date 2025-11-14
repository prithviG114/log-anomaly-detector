import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api, LogEntry } from '../services/api'
import LogDetailModal from '../components/LogDetailModal'
import { getSeverity } from '../utils/severity'
import './Visualizations.css'

export default function Visualizations() {
  const [anomalies, setAnomalies] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null)
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([])

  useEffect(() => {
    fetchAnomalies()
  }, [])

  const fetchAnomalies = async () => {
    try {
      setLoading(true)
      const data = await api.getAnomalies()
      setAnomalies(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch anomalies. Make sure the backend is running.')
      console.error('Error fetching anomalies:', err)
    } finally {
      setLoading(false)
    }
  }

  // Process data for charts
  const getTimeSeriesData = () => {
    const grouped = anomalies.reduce((acc, log) => {
      const date = new Date(log.timestamp).toLocaleDateString()
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return Object.entries(grouped)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(-10) // Last 10 days
  }

  const getServiceData = () => {
    const grouped = anomalies.reduce((acc, log) => {
      acc[log.serviceName] = (acc[log.serviceName] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return Object.entries(grouped)
      .map(([service, count]) => ({ service, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5) // Top 5 services
  }

  const getCategoryData = () => {
    const categories = anomalies.reduce((acc, log) => {
      const msg = log.message.toLowerCase()
      let category = 'Other'
      
      if (msg.includes('error') || msg.includes('exception')) category = 'Errors'
      else if (msg.includes('timeout')) category = 'Timeouts'
      else if (msg.includes('connection') || msg.includes('unavailable')) category = 'Connection Issues'
      else if (msg.includes('fail')) category = 'Failures'
      
      acc[category] = (acc[category] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return Object.entries(categories).map(([name, value]) => ({ name, value }))
  }

  const COLORS = ['#ffb86b', '#ff7c93', '#8ea7c0', '#a78bfa', '#34d399']

  const handleServiceClick = (serviceName: string) => {
    const logs = anomalies.filter(a => a.serviceName === serviceName)
    setFilteredLogs(logs)
  }

  const handleCategoryClick = (category: string) => {
    const logs = anomalies.filter(a => {
      const msg = a.message.toLowerCase()
      if (category === 'Errors' && (msg.includes('error') || msg.includes('exception'))) return true
      if (category === 'Timeouts' && msg.includes('timeout')) return true
      if (category === 'Connection Issues' && (msg.includes('connection') || msg.includes('unavailable'))) return true
      if (category === 'Failures' && msg.includes('fail')) return true
      if (category === 'Other') return !msg.includes('error') && !msg.includes('exception') && !msg.includes('timeout') && !msg.includes('connection') && !msg.includes('unavailable') && !msg.includes('fail')
      return false
    })
    setFilteredLogs(logs)
  }

  if (loading) {
    return (
      <main>
        <div className="glass">
          <h1>Visualization Dashboard</h1>
          <div className="loading-state">Loading anomaly data...</div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main>
        <div className="glass">
          <h1>Visualization Dashboard</h1>
          <div className="error-state">
            <p>{error}</p>
            <button onClick={fetchAnomalies} className="btn primary">Retry</button>
          </div>
        </div>
      </main>
    )
  }

  if (anomalies.length === 0) {
    return (
      <main>
        <div className="glass">
          <h1>Visualization Dashboard</h1>
          <div className="empty-state">
            <p>No anomalies detected yet. Start sending logs to see visualizations.</p>
            <Link to="/" className="btn primary">Back to Details</Link>
          </div>
        </div>
      </main>
    )
  }

  const timeSeriesData = getTimeSeriesData()
  const serviceData = getServiceData()
  const categoryData = getCategoryData()

  return (
    <main>
      <div className="glass">
        <div className="header-row">
          <h1>Visualization Dashboard</h1>
          <button onClick={fetchAnomalies} className="btn refresh">🔄 Refresh</button>
        </div>
        <p>
          Explore the graphical summary of detected anomalies, frequency trends, and log category 
          distributions generated from the analysis.
        </p>
        
        <div className="stats-row">
          <div className="stat-box">
            <div className="stat-value">{anomalies.length}</div>
            <div className="stat-label">Total Anomalies</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{new Set(anomalies.map(a => a.serviceName)).size}</div>
            <div className="stat-label">Affected Services</div>
          </div>
        </div>

        <div className="grid">
          <div className="chart-card">
            <h3>📊 Anomalies over Time</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="var(--muted)" style={{ fontSize: '12px' }} />
                <YAxis stroke="var(--muted)" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(27, 26, 32, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#f8f8f8'
                  }} 
                />
                <Line type="monotone" dataKey="count" stroke="#ff7c93" strokeWidth={2} dot={{ fill: '#ff7c93' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>🍩 Anomaly Categories</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                  label={(entry) => entry.name}
                  labelLine={{ stroke: '#ffffff' }}
                  onClick={(data) => handleCategoryClick(data.name)}
                  cursor="pointer"
                >
                  {categoryData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(27, 26, 32, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#ffffff'
                  }}
                  itemStyle={{
                    color: '#ffffff'
                  }}
                  labelStyle={{
                    color: '#ffffff'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card full-width">
            <h3>📈 Service-wise Anomaly Density</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={serviceData} onClick={(data) => {
                if (data && data.activePayload && data.activePayload[0]) {
                  handleServiceClick(data.activePayload[0].payload.service)
                }
              }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="service" stroke="var(--muted)" style={{ fontSize: '12px' }} />
                <YAxis stroke="var(--muted)" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(27, 26, 32, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#f8f8f8'
                  }}
                  cursor={{ fill: 'rgba(255, 184, 107, 0.1)' }}
                />
                <Bar 
                  dataKey="count" 
                  fill="#ffb86b" 
                  radius={[8, 8, 0, 0]} 
                  cursor="pointer"
                  activeBar={{ fill: '#ff9d4d' }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {filteredLogs.length > 0 && (
          <div className="filtered-logs">
            <h3>Filtered Logs ({filteredLogs.length})</h3>
            <div className="log-grid">
              {filteredLogs.slice(0, 10).map(log => (
                <div 
                  key={log.id} 
                  className="log-card"
                  onClick={() => setSelectedLog(log)}
                >
                  <div className="log-card-header">
                    <span className="log-card-service">{log.serviceName}</span>
                    <span className="log-card-time">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="log-card-message">{log.message}</div>
                  <div className="log-card-footer">
                    <span 
                      className="severity-pill"
                      style={{
                        color: getSeverity(log.score, log.isAnomaly).color,
                        background: getSeverity(log.score, log.isAnomaly).bgColor,
                        borderColor: getSeverity(log.score, log.isAnomaly).borderColor
                      }}
                    >
                      {getSeverity(log.score, log.isAnomaly).label}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: '40px' }}>
          <Link to="/" className="btn primary">Back to Details</Link>
        </div>
      </div>
      
      <LogDetailModal log={selectedLog} onClose={() => setSelectedLog(null)} />
    </main>
  )
}
