import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api, LogEntry } from '../services/api'
import LogDetailModal from '../components/LogDetailModal'
import './About.css'

export default function About() {
  const [stats, setStats] = useState({
    totalLogs: 0,
    totalAnomalies: 0,
    services: 0
  })
  const [recentLogs, setRecentLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const [logs, anomalies] = await Promise.all([
        api.getLogs({ limit: 10 }),
        api.getAnomalies()
      ])
      
      const uniqueServices = new Set(logs.map(log => log.serviceName))
      
      setStats({
        totalLogs: logs.length,
        totalAnomalies: anomalies.length,
        services: uniqueServices.size
      })
      
      setRecentLogs(logs.slice(0, 5))
    } catch (err) {
      console.error('Error fetching stats:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <section className="glass">
        <h1>About Log Anomaly Detector</h1>
        <p>
          This project uses machine learning to analyze collected log data from microservice-based systems. 
          Instead of real-time detection, it processes logs offline to identify unusual patterns and events 
          that signal system anomalies.
        </p>

        {!loading && stats.totalLogs > 0 && (
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">{stats.totalLogs}</div>
              <div className="stat-text">Recent Logs</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.totalAnomalies}</div>
              <div className="stat-text">Anomalies Detected</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.services}</div>
              <div className="stat-text">Active Services</div>
            </div>
          </div>
        )}

        <div className="grid">
          <div className="card">
            <strong>🔍 ML Insights</strong>
            <p>AI models highlight unseen log behaviors.</p>
          </div>
          <div className="card">
            <strong>📦 Container Support</strong>
            <p>Designed for Docker and Kubernetes environments.</p>
          </div>
          <div className="card">
            <strong>⚙️ Configurable</strong>
            <p>Thresholds and features are customizable to match infrastructure needs.</p>
          </div>
        </div>

        {recentLogs.length > 0 && (
          <div className="recent-logs">
            <h3>Recent Log Activity</h3>
            <div className="log-list">
              {recentLogs.map(log => (
                <div 
                  key={log.id} 
                  className={`log-item ${log.isAnomaly ? 'anomaly' : ''}`}
                  onClick={() => setSelectedLog(log)}
                >
                  <span className="log-service">{log.serviceName}</span>
                  <span className="log-message">{log.message}</span>
                  {log.isAnomaly && <span className="anomaly-badge">⚠️</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        <LogDetailModal log={selectedLog} onClose={() => setSelectedLog(null)} />

        <div style={{ marginTop: '28px', textAlign: 'center' }}>
          <Link to="/visualizations" className="btn primary">View Visualizations</Link>
        </div>
      </section>
    </main>
  )
}
