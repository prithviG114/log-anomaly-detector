export type SeverityLevel = 'critical' | 'severe' | 'moderate' | 'low' | 'normal'

export interface Severity {
  level: SeverityLevel
  label: string
  color: string
  bgColor: string
  borderColor: string
}

/**
 * Convert raw anomaly score to 1-10 scale
 * Raw scores from Isolation Forest are typically between -1 and 1
 * Lower (more negative) = more anomalous = higher score (1-10)
 * 
 * @param rawScore - Raw ML score (typically -1 to 1)
 * @returns Score from 1 (normal) to 10 (critical)
 */
export function convertToTenScale(rawScore: number): number {
  // Clamp score to reasonable range
  const clampedScore = Math.max(-1, Math.min(1, rawScore))
  
  // Convert: -1 (most anomalous) -> 10, 0 (neutral) -> 5, 1 (normal) -> 1
  // Formula: 10 - ((score + 1) * 4.5)
  const tenScale = 10 - ((clampedScore + 1) * 4.5)
  
  // Round to 1 decimal place
  return Math.round(tenScale * 10) / 10
}

/**
 * Classify anomaly severity based on score
 * Lower scores = more anomalous = higher severity
 * Score ranges (typical for Isolation Forest):
 * < -0.5: Critical
 * -0.5 to -0.2: Severe
 * -0.2 to -0.05: Moderate
 * -0.05 to 0: Low
 * >= 0: Normal
 */
export function getSeverity(score: number, _isAnomaly: boolean): Severity {
  // Classify primarily by score (lower = more severe)
  if (score < -0.5) {
    return {
      level: 'critical',
      label: 'Critical',
      color: '#ef4444',
      bgColor: 'rgba(239, 68, 68, 0.15)',
      borderColor: 'rgba(239, 68, 68, 0.4)'
    }
  }

  if (score < -0.2) {
    return {
      level: 'severe',
      label: 'Severe',
      color: '#f97316',
      bgColor: 'rgba(249, 115, 22, 0.15)',
      borderColor: 'rgba(249, 115, 22, 0.3)'
    }
  }

  if (score < -0.05) {
    return {
      level: 'moderate',
      label: 'Moderate',
      color: '#fbbf24',
      bgColor: 'rgba(251, 191, 36, 0.15)',
      borderColor: 'rgba(251, 191, 36, 0.3)'
    }
  }

  if (score < 0) {
    return {
      level: 'low',
      label: 'Low',
      color: '#60a5fa',
      bgColor: 'rgba(96, 165, 250, 0.15)',
      borderColor: 'rgba(96, 165, 250, 0.3)'
    }
  }

  // Score >= 0 means normal
  return {
    level: 'normal',
    label: 'Normal',
    color: '#6ee7b7',
    bgColor: 'rgba(16, 185, 129, 0.15)',
    borderColor: 'rgba(16, 185, 129, 0.3)'
  }
}
