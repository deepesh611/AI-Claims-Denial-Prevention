import { Card, CardContent } from "@/components/ui/card"
import type { ClaimResult } from "@/lib/types"

interface SummaryMetricsProps {
  results: ClaimResult[]
}

export function SummaryMetrics({ results }: SummaryMetricsProps) {
  const total = results.length
  const highRisk = results.filter((r) => r.risk_level?.toLowerCase()?.trim() === "high").length
  const passed = results.filter((r) => r.risk_level?.toLowerCase()?.trim() === "low").length
  const ruleFail = results.filter((r) => {
    const level = r.risk_level?.toLowerCase()?.trim()
    return level !== "high" && level !== "low"
  }).length

  const metrics = [
    {
      label: "Total Claims",
      value: total,
      color: "text-foreground",
      bgColor: "bg-muted",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5" aria-hidden="true">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
    },
    {
      label: "High Risk",
      value: highRisk,
      color: "text-red-700",
      bgColor: "bg-red-50",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5" aria-hidden="true">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
    },
    {
      label: "Rule Failures",
      value: ruleFail,
      color: "text-yellow-700",
      bgColor: "bg-yellow-50",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      ),
    },
    {
      label: "Passed",
      value: passed,
      color: "text-green-700",
      bgColor: "bg-green-50",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5" aria-hidden="true">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ),
    },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {metrics.map((m) => (
        <Card key={m.label} className="border-border shadow-none">
          <CardContent className="p-4 flex flex-col gap-3">
            <div className={`inline-flex items-center justify-center w-9 h-9 rounded-lg ${m.bgColor} ${m.color}`}>
              {m.icon}
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{m.value}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{m.label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
