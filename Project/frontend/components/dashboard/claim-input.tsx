"use client"

import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface ClaimInputProps {
  onAnalyze: (claimIds: string[]) => void
  isLoading: boolean
}

export function ClaimInput({ onAnalyze, isLoading }: ClaimInputProps) {
  const [claimId, setClaimId] = useState("")
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvError, setCsvError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function parseCsv(text: string): string[] {
    const lines = text.trim().split(/\r?\n/)
    if (lines.length === 0) return []

    const header = lines[0].toLowerCase().trim()
    const headerCols = header.split(",").map((h) => h.trim())
    const claimIdIndex = headerCols.indexOf("claim_id")

    if (claimIdIndex === -1) {
      throw new Error('CSV must contain a "claim_id" column header')
    }

    return lines
      .slice(1)
      .map((line) => {
        const cols = line.split(",")
        return cols[claimIdIndex]?.trim() ?? ""
      })
      .filter(Boolean)
  }

  function handleFileChange(file: File | null) {
    setCsvError(null)
    setCsvFile(file)
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith(".csv")) {
      handleFileChange(file)
    } else {
      setCsvError("Please upload a valid .csv file")
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setCsvError(null)

    if (csvFile) {
      try {
        const text = await csvFile.text()
        const ids = parseCsv(text)
        if (ids.length === 0) {
          setCsvError("No valid claim IDs found in the CSV file")
          return
        }
        onAnalyze(ids)
      } catch (err) {
        setCsvError(err instanceof Error ? err.message : "Failed to parse CSV")
      }
      return
    }

    const trimmed = claimId.trim()
    if (!trimmed) return
    onAnalyze([trimmed])
  }

  const canSubmit = (claimId.trim().length > 0 || csvFile !== null) && !isLoading

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {/* Single claim input */}
      <div className="flex flex-col gap-2">
        <Label htmlFor="claim-id" className="text-sm font-medium">
          Claim ID
        </Label>
        <div className="flex gap-2">
          <Input
            id="claim-id"
            type="text"
            placeholder="e.g. C01220"
            value={claimId}
            onChange={(e) => {
              setClaimId(e.target.value)
              if (e.target.value) setCsvFile(null)
            }}
            disabled={csvFile !== null || isLoading}
            className="flex-1 font-mono text-sm"
          />
        </div>
        <p className="text-xs text-muted-foreground">Enter a single claim ID for individual analysis</p>
      </div>

      {/* Divider */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-px bg-border" />
        <span className="text-xs text-muted-foreground font-medium">OR</span>
        <div className="flex-1 h-px bg-border" />
      </div>

      {/* CSV upload */}
      <div className="flex flex-col gap-2">
        <Label className="text-sm font-medium">
          Bulk CSV Upload
        </Label>
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => !isLoading && !claimId && fileInputRef.current?.click()}
          className={cn(
            "relative flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-6 py-8 cursor-pointer transition-colors",
            isDragging
              ? "border-primary bg-primary/5"
              : csvFile
              ? "border-primary/50 bg-primary/5"
              : "border-border hover:border-primary/50 hover:bg-muted/50",
            (isLoading || claimId) && "opacity-50 pointer-events-none"
          )}
          role="button"
          tabIndex={0}
          aria-label="Upload CSV file"
          onKeyDown={(e) => e.key === "Enter" && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="sr-only"
            onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
            disabled={isLoading || !!claimId}
          />
          {csvFile ? (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8 text-primary" aria-hidden="true">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">{csvFile.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {(csvFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setCsvFile(null); setCsvError(null) }}
                className="text-xs text-muted-foreground underline hover:text-foreground"
              >
                Remove file
              </button>
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8 text-muted-foreground" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">
                  Drop CSV here or click to browse
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  File must have a <code className="font-mono">claim_id</code> column
                </p>
              </div>
            </>
          )}
        </div>
        {csvError && (
          <p className="text-xs text-destructive flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {csvError}
          </p>
        )}
        <p className="text-xs text-muted-foreground">
          Upload a CSV with multiple claim IDs for batch analysis
        </p>
      </div>

      {/* Submit */}
      <Button
        type="submit"
        disabled={!canSubmit}
        className="w-full h-10 font-medium"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Running Analysis...
          </span>
        ) : (
          "Run Analysis"
        )}
      </Button>
    </form>
  )
}
