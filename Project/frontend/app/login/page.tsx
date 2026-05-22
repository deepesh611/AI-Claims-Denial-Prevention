"use client"

import { signIn } from "next-auth/react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)

  async function handleSignIn() {
    setIsLoading(true)
    await signIn("google", { callbackUrl: "/" })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md flex flex-col items-center gap-8">
        {/* Branding */}
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-primary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-7 h-7 text-primary-foreground"
              aria-hidden="true"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground text-balance">
              AI Claim Denial Prevention System
            </h1>
            <p className="mt-1 text-sm text-muted-foreground text-pretty">
              Predict and prevent healthcare claim denials with AI-powered analysis
            </p>
          </div>
        </div>

        {/* Card */}
        <Card className="w-full shadow-sm border-border">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-lg font-semibold">Sign in to continue</CardTitle>
            <CardDescription className="text-sm text-muted-foreground">
              Use your organization&apos;s Google account to access the platform
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <Button
              onClick={handleSignIn}
              disabled={isLoading}
              className="w-full h-11 gap-3 text-sm font-medium"
              variant="outline"
            >
              {isLoading ? (
                <svg
                  className="w-4 h-4 animate-spin"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className="w-5 h-5"
                  aria-hidden="true"
                >
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
              )}
              {isLoading ? "Signing in..." : "Sign in with Google"}
            </Button>

            <p className="text-xs text-center text-muted-foreground leading-relaxed">
              By signing in, you agree to use this platform in accordance with your
              organization&apos;s data policies and HIPAA guidelines.
            </p>
          </CardContent>
        </Card>

        <p className="text-xs text-muted-foreground text-center">
          Powered by AI &middot; HIPAA-compliant infrastructure
        </p>
      </div>
    </div>
  )
}
