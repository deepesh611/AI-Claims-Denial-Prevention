"use client"

import { SummaryMetrics } from "@/components/dashboard/summary-metrics"
import { ClaimCard } from "@/components/dashboard/claim-card"
import type { ClaimResult } from "@/lib/types"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"

interface ResultsSectionProps {
  results: ClaimResult[]
  error: string | null
}

export function ResultsSection({ results, error }: ResultsSectionProps) {
  const handleExportCSV = () => {
    if (results.length === 0) return

    const headers = [
      "Claim ID",
      "Status",
      "Risk Score (%)",
      "Risk Level",
      "Rule Failures",
      "Primary Reason",
      "Secondary Reason",
      "Policy Violated",
      "AI Recommendation"
    ]

    const rows = results.map((claim) => [
      claim.claim_id,
      claim.status ?? "",
      claim.risk_score !== undefined ? `${Math.round(claim.risk_score * 100)}` : "",
      claim.risk_level ?? "",
      claim.rule_failures ? claim.rule_failures.join("; ") : "",
      claim.reason_1 ?? "",
      claim.reason_2 ?? "",
      claim.policy_violated ?? "",
      claim.ai_recommendation ?? ""
    ])

    const csvContent = [
      headers.join(","),
      ...rows.map((row) =>
        row
          .map((val) => {
            const escaped = String(val).replace(/"/g, '""')
            return `"${escaped}"`
          })
          .join(",")
      )
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.setAttribute("href", url)
    link.setAttribute("download", `claim_analysis_results_${new Date().toISOString().slice(0, 10)}.csv`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleExportJSON = () => {
    if (results.length === 0) return

    const jsonString = JSON.stringify(results, null, 2)
    const blob = new Blob([jsonString], { type: "application/json;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.setAttribute("href", url)
    link.setAttribute("download", `claim_analysis_results_${new Date().toISOString().slice(0, 10)}.json`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

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
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-base font-semibold text-foreground mb-1">Analysis Results</h2>
          <p className="text-sm text-muted-foreground">
            {results.length} claim{results.length !== 1 ? "s" : ""} analyzed
          </p>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="gap-2 border-border/80 shadow-xs hover:bg-accent/50 cursor-pointer">
              <Download className="w-4 h-4 text-muted-foreground" />
              <span>Export Results</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 bg-popover text-popover-foreground border border-border rounded-md p-1 shadow-md z-50">
            <DropdownMenuLabel className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">Choose Format</DropdownMenuLabel>
            <DropdownMenuSeparator className="h-px bg-border my-1" />
            <DropdownMenuItem onClick={handleExportCSV} className="cursor-pointer gap-2 px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-muted-foreground" aria-hidden="true">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <path d="M8 13h8" />
                <path d="M8 17h8" />
                <path d="M10 9H9" />
              </svg>
              <span>Export CSV</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleExportJSON} className="cursor-pointer gap-2 px-2 py-1.5 text-sm rounded-sm hover:bg-accent hover:text-accent-foreground flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-muted-foreground" aria-hidden="true">
                <path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v1" />
                <path d="M18 8h4a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-4" />
                <path d="M21 12H18" />
              </svg>
              <span>Export JSON</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
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

