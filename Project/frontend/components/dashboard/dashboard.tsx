"use client"

import { useState } from "react"
import type { Session } from "next-auth"
import { Header } from "@/components/dashboard/header"
import { ClaimInput } from "@/components/dashboard/claim-input"
import { ResultsSection } from "@/components/dashboard/results-section"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { ClaimResult } from "@/lib/types"

interface DashboardProps {
  session: Session
}

export function Dashboard({ session }: DashboardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ClaimResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const [hasRun, setHasRun] = useState(false)

  async function handleAnalyze(claimIds: string[]) {
    setIsLoading(true)
    setError(null)
    setResults([])
    setHasRun(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL
      if (!apiUrl) {
        throw new Error("API URL is not configured. Please set NEXT_PUBLIC_API_URL.")
      }

      const response = await fetch(`${apiUrl}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim_ids: claimIds }),
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error")
        throw new Error(`API error (${response.status}): ${errorText}`)
      }

      const data = await response.json()

      // Support both { results: [...] } and [...] response shapes
      const claimResults: ClaimResult[] = Array.isArray(data) ? data : data.results ?? []
      setResults(claimResults)
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred"
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header session={session} />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col gap-8">
          {/* Page title */}
          <div>
            <h1 className="text-2xl font-bold text-foreground text-balance">
              Claim Denial Analysis
            </h1>
            <p className="mt-1 text-sm text-muted-foreground text-pretty">
              Submit claim IDs to receive AI-powered denial risk predictions and actionable recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Input panel */}
            <div className="lg:col-span-1">
              <Card className="border-border shadow-none sticky top-24">
                <CardHeader className="pb-4">
                  <CardTitle className="text-sm font-semibold">Submit Claims</CardTitle>
                  <CardDescription className="text-xs">
                    Enter a single claim ID or upload a CSV file for batch analysis.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ClaimInput onAnalyze={handleAnalyze} isLoading={isLoading} />
                </CardContent>
              </Card>
            </div>

            {/* Results panel */}
            <div className="lg:col-span-2">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                  <div className="relative">
                    <svg className="w-10 h-10 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-label="Loading">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-semibold text-foreground">Running AI Analysis</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Evaluating claim risk factors and policy compliance...
                    </p>
                  </div>
                </div>
              ) : (
                <ResultsSection results={results} error={hasRun ? error : null} />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
