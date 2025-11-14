import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8080'

export interface LogEntry {
  id: string
  serviceName: string
  message: string
  timestamp: number
  isAnomaly: boolean
  score: number
}

export const api = {
  // Fetch all logs
  async getLogs(params?: {
    serviceName?: string
    since?: number
    until?: number
    limit?: number
  }): Promise<LogEntry[]> {
    const response = await axios.get(`${API_BASE_URL}/logs`, { params })
    return response.data
  },

  // Fetch only anomalies
  async getAnomalies(): Promise<LogEntry[]> {
    const response = await axios.get(`${API_BASE_URL}/logs/anomalies`)
    return response.data
  },

  // Add a new log
  async addLog(log: { serviceName: string; message: string }): Promise<LogEntry> {
    const response = await axios.post(`${API_BASE_URL}/logs`, log)
    return response.data
  },

  // Add multiple logs
  async addLogsBatch(logs: Array<{ serviceName: string; message: string }>): Promise<LogEntry[]> {
    const response = await axios.post(`${API_BASE_URL}/logs/batch`, logs)
    return response.data
  }
}
