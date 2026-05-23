// lib/types.ts

export interface ClaimResult {
  claim_id: string
  status?: string
  risk_score?: number
  risk_label?: string
  risk_level?: string
  rule_failures?: string[]
  reason_1?: string
  reason_2?: string
  policy_violated?: string
  policy_text?: string
  risk_reasons?: string[]
  ai_recommendation?: string
}
