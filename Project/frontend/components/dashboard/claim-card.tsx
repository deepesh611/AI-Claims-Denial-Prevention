import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import type { ClaimResult } from "@/lib/types"
import { cn } from "@/lib/utils"

interface ClaimCardProps {
  claim: ClaimResult
}


function getRiskConfig(riskLevel: string) {
  const level = riskLevel?.toLowerCase()?.trim()
  if (level === "high") {
    return {
      label: "HIGH RISK",
      badgeClass: "bg-red-100 text-red-700 border-red-200 hover:bg-red-100",
      progressClass: "bg-red-500",
      borderClass: "border-l-red-500",
    }
  }
  if (level === "low") {
    return {
      label: "LOW RISK",
      badgeClass: "bg-green-100 text-green-700 border-green-200 hover:bg-green-100",
      progressClass: "bg-green-500",
      borderClass: "border-l-green-500",
    }
  }
  // Any other value (rule_fail, failed, denied, medium, or any unknown backend value)
  // is treated as a rule failure — never silently pass as Low Risk
  return {
    label: "RULE FAIL",
    badgeClass: "bg-yellow-100 text-yellow-700 border-yellow-200 hover:bg-yellow-100",
    progressClass: "bg-yellow-500",
    borderClass: "border-l-yellow-500",
  }
}

export function ClaimCard({ claim }: ClaimCardProps) {
  const config = getRiskConfig(claim.risk_level)
  const score = Math.round((claim.risk_score ?? 0) * 100)

  return (
    <Card className={cn("border-l-4 shadow-none", config.borderClass)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <p className="font-bold text-base text-foreground font-mono tracking-wide">
            {claim.claim_id}
          </p>
          <Badge
            variant="outline"
            className={cn("text-xs font-semibold px-2.5 py-0.5", config.badgeClass)}
          >
            {config.label}
          </Badge>
        </div>

        {/* Risk Score */}
        <div className="mt-3 flex flex-col gap-1.5">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground font-medium">Risk Score</span>
            <span className="text-xs font-bold text-foreground">{score}%</span>
          </div>
          <div className="relative h-2 w-full rounded-full bg-muted overflow-hidden">
            <div
              className={cn("h-full rounded-full transition-all", config.progressClass)}
              style={{ width: `${score}%` }}
              role="progressbar"
              aria-valuenow={score}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`Risk score: ${score}%`}
            />
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0 flex flex-col gap-4">
        {/* Risk Reasons */}
        {claim.risk_reasons && claim.risk_reasons.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              Top Risk Reasons
            </p>
            <ul className="flex flex-col gap-1.5">
              {claim.risk_reasons.map((reason, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                  <span className="mt-1.5 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-muted-foreground" aria-hidden="true" />
                  {reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Policy Violated */}
        {claim.policy_violated && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
              Policy Violated
            </p>
            <p className="text-sm text-foreground italic leading-relaxed">
              {claim.policy_violated}
            </p>
          </div>
        )}

        {/* AI Recommendation */}
        {claim.ai_recommendation && (
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1.5 flex items-center gap-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5" aria-hidden="true">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="16" />
                <line x1="8" y1="12" x2="16" y2="12" />
              </svg>
              AI Recommendation
            </p>
            <p className="text-sm text-foreground leading-relaxed">
              {claim.ai_recommendation}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
