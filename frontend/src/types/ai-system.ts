/**
 * AI System types matching the backend SQLAlchemy model exactly.
 */

export type RiskClassification =
  | 'PROHIBITED'
  | 'HIGH_RISK'
  | 'LIMITED_TRANSPARENCY'
  | 'MINIMAL_OR_NO_RISK'
  | 'NEEDS_REVIEW'

export type AISystemStatus =
  | 'DISCOVERED'
  | 'DRAFT'
  | 'IN_REVIEW'
  | 'APPROVED'
  | 'ACTIVE'
  | 'SUSPENDED'
  | 'RETIRED'

export type DeploymentEnvironment =
  | 'production'
  | 'staging'
  | 'development'
  | 'testing'

export type BusinessDomain =
  | 'hr'
  | 'finance'
  | 'legal'
  | 'operations'
  | 'sales'
  | 'marketing'
  | 'customer_service'
  | 'it'
  | 'research'
  | 'product'
  | 'security'
  | 'other'

export const DATA_CATEGORIES = [
  'personal_data',
  'sensitive_personal_data',
  'financial_data',
  'health_data',
  'biometric_data',
  'behavioral_data',
  'location_data',
  'professional_data',
  'public_data',
  'anonymous_data',
] as const

export type DataCategory = (typeof DATA_CATEGORIES)[number]

export interface AISystem {
  id: string
  organization_id: string
  name: string
  description: string | null
  business_purpose: string | null
  owner_id: string | null
  owner_name: string | null
  department: string | null
  provider: string | null
  model_name: string | null
  model_version: string | null
  deployment_environment: DeploymentEnvironment | null
  business_domain: BusinessDomain | null
  data_categories: DataCategory[]
  risk_classification: RiskClassification
  lifecycle_status: AISystemStatus
  regulatory_status: string | null
  review_date: string | null
  created_at: string
  updated_at: string
}

export interface CreateAISystemRequest {
  name: string
  description?: string | null
  business_purpose?: string | null
  department?: string | null
  provider?: string | null
  model_name?: string | null
  model_version?: string | null
  deployment_environment?: DeploymentEnvironment | null
  business_domain?: BusinessDomain | null
  data_categories?: DataCategory[]
}

export interface UpdateAISystemRequest extends Partial<CreateAISystemRequest> {
  lifecycle_status?: AISystemStatus
  risk_classification?: RiskClassification
  review_date?: string | null
}

export interface AISystemListParams {
  page?: number
  page_size?: number
  search?: string
  risk_classification?: RiskClassification | ''
  lifecycle_status?: AISystemStatus | ''
  department?: string
}

/** Human-readable labels for enums */
export const RISK_LABELS: Record<RiskClassification, string> = {
  PROHIBITED: 'Prohibited',
  HIGH_RISK: 'High Risk',
  LIMITED_TRANSPARENCY: 'Limited Transparency',
  MINIMAL_OR_NO_RISK: 'Minimal Risk',
  NEEDS_REVIEW: 'Needs Review',
}

export const STATUS_LABELS: Record<AISystemStatus, string> = {
  DISCOVERED: 'Discovered',
  DRAFT: 'Draft',
  IN_REVIEW: 'In Review',
  APPROVED: 'Approved',
  ACTIVE: 'Active',
  SUSPENDED: 'Suspended',
  RETIRED: 'Retired',
}

export const BUSINESS_DOMAIN_LABELS: Record<BusinessDomain, string> = {
  hr: 'Human Resources',
  finance: 'Finance',
  legal: 'Legal',
  operations: 'Operations',
  sales: 'Sales',
  marketing: 'Marketing',
  customer_service: 'Customer Service',
  it: 'Information Technology',
  research: 'Research & Development',
  product: 'Product',
  security: 'Security',
  other: 'Other',
}
