/**
 * Shared API response envelope types used across all API calls.
 */

/** Standard paginated list response from the backend */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

/** Standard API error response */
export interface APIError {
  detail: string
  code?: string
  field?: string
}

/** Standard success response with optional data */
export interface APISuccess<T = void> {
  data: T
  message?: string
}

/** Audit event types for filtering */
export type AuditAction =
  | 'CREATE'
  | 'UPDATE'
  | 'DELETE'
  | 'VIEW'
  | 'LOGIN'
  | 'LOGOUT'
  | 'APPROVE'
  | 'REJECT'
  | 'SUBMIT'
  | 'ARCHIVE'
  | 'EXPORT'
  | 'IMPORT'

/** An audit event as returned by the API */
export interface AuditEvent {
  id: string
  organization_id: string
  actor_id: string
  actor_email: string
  actor_name: string
  action: AuditAction
  resource_type: string
  resource_id: string | null
  resource_name: string | null
  changes: Record<string, unknown> | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

/** Dashboard summary metrics returned by the overview endpoint */
export interface DashboardMetrics {
  ai_systems_count: number
  high_risk_systems_count: number
  open_gaps_count: number
  stale_evidence_count: number
  active_incidents_count: number
  pending_approvals_count: number
  training_overdue_count: number
  upcoming_reviews_count: number
}

/** Compliance area status for the dashboard table */
export interface ComplianceArea {
  id: string
  name: string
  description: string
  status: 'PASS' | 'FAIL' | 'REVIEW' | 'UNKNOWN'
  last_reviewed_at: string | null
  gap_count: number
  control_count: number
}
