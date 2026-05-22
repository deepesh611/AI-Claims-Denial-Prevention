import { SummaryMetrics } from "@/components/dashboard/summary-metrics"
import { ClaimCard } from "@/components/dashboard/claim-card"
import type { ClaimResult } from "@/lib/types"

interface ResultsSectionProps {
  results: ClaimResult[]
  error: string | null
}

export function ResultsSection({ results, error }: ResultsSectionProps) {
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3 text-center">
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-50">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6 text-red-600" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground">Analysis Failed</p>
          <p className="text-sm text-muted-foreground mt-1 max-w-md">{error}</p>
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-muted">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6 text-muted-foreground" aria-hidden="true">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground">No results yet</p>
          <p className="text-sm text-muted-foreground mt-1">
            Enter claim IDs above and click &quot;Run Analysis&quot; to get started
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-base font-semibold text-foreground mb-1">Analysis Results</h2>
        <p className="text-sm text-muted-foreground">
          {results.length} claim{results.length !== 1 ? "s" : ""} analyzed
        </p>
      </div>
      <SummaryMetrics results={results} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {results.map((claim) => (
          <ClaimCard key={claim.claim_id} claim={claim} />
        ))}
      </div>
    </div>
  )
}
