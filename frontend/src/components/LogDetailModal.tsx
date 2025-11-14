import { LogEntry } from '../services/api'
import { getSeverity, convertToTenScale } from '../utils/severity'
import './LogDetailModal.css'

interface Props {
  log: LogEntry | null
  onClose: () => void
}

export default function LogDetailModal({ log, onClose }: Props) {
  if (!log) return null

  const formatTimestamp = (ts: number) => {
    return new Date(ts).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Details</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        
        <div className="modal-body">
          <div className="detail-row">
            <span className="detail-label">ID</span>
            <span className="detail-value mono">{log.id}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Service</span>
            <span className="detail-value service-badge">{log.serviceName}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Timestamp</span>
            <span className="detail-value">{formatTimestamp(log.timestamp)}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Severity Level</span>
            <span 
              className="detail-value severity-badge"
              style={{
                color: getSeverity(log.score, log.isAnomaly).color,
                background: getSeverity(log.score, log.isAnomaly).bgColor,
                borderColor: getSeverity(log.score, log.isAnomaly).borderColor
              }}
            >
              {getSeverity(log.score, log.isAnomaly).label}
            </span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Anomaly Score</span>
            <span className="detail-value">
              <span className="score-display">{convertToTenScale(log.score)}</span>
              <span className="score-scale"> / 10</span>
            </span>
          </div>
          
          <div className="detail-row full-width">
            <span className="detail-label">Message</span>
            <div className="message-box">{log.message}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
