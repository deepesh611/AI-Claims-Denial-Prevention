export interface ClaimResult {
  claim_id: string
  status: string
  risk_score: number | null
  risk_label: string | null
  risk_level: string // "high", "low", "rule_fail", etc.
  rule_failures: string[]
  reason_1: string | null
  reason_2: string | null
  policy_violated: string | null
  policy_text: string | null
  risk_reasons: string[]
  ai_recommendation: string | null
}
