/**
 * Auth-related types matching the backend user/org models.
 */

export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface Organization {
  id: string
  name: string
  slug: string
  plan: 'FREE' | 'STARTER' | 'PROFESSIONAL' | 'ENTERPRISE'
  is_active: boolean
  created_at: string
}

export interface OrganizationMembership {
  id: string
  user_id: string
  organization_id: string
  role: 'OWNER' | 'ADMIN' | 'ANALYST' | 'VIEWER'
  created_at: string
  organization: Organization
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export interface AuthResponse {
  user: User
  token: TokenResponse
  membership: OrganizationMembership
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  organization_name: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  new_password: string
}
