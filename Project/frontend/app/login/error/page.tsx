'use client'

import { Suspense } from 'react'
import { Button } from '@/components/ui/button'
import { useSearchParams } from 'next/navigation'

function ErrorContent() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  const getErrorMessage = () => {
    switch (error) {
      case 'AccessDenied':
        return 'Access Denied: Your email is not authorized to access this application.'
      case 'OAuthSignin':
      case 'OAuthCallback':
      case 'OAuthCreateAccount':
      case 'EmailCreateAccount':
      case 'Callback':
        return 'There was an error with the sign-in process. Please try again.'
      case 'EmailSignInError':
        return 'Could not sign in with that email.'
      case 'SessionCallback':
        return 'Session error. Please try signing in again.'
      default:
        return 'An error occurred during authentication. Please try again.'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-secondary flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-card border border-border rounded-lg shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-destructive/10">
              <svg className="w-6 h-6 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>

          <h1 className="text-2xl font-bold text-card-foreground mb-2">
            Authentication Error
          </h1>
          <p className="text-muted-foreground mb-6">
            {getErrorMessage()}
          </p>

          <Button
            onClick={() => (window.location.href = '/login')}
            className="w-full"
          >
            Back to Sign In
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function AuthError() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-background to-secondary flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    }>
      <ErrorContent />
    </Suspense>
  )
}
