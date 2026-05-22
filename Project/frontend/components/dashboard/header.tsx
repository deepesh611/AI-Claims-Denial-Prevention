"use client"

import { signOut } from "next-auth/react"
import { useState } from "react"
import type { Session } from "next-auth"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface HeaderProps {
  session: Session
}

export function Header({ session }: HeaderProps) {
  const [signingOut, setSigningOut] = useState(false)

  async function handleSignOut() {
    setSigningOut(true)
    await signOut({ callbackUrl: "/login" })
  }

  const user = session.user
  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "U"

  return (
    <header className="sticky top-0 z-10 bg-card border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Logo + Title */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary flex-shrink-0">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-5 h-5 text-primary-foreground"
              aria-hidden="true"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-semibold text-foreground leading-none">
              AI Claim Denial Prevention
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              Powered by machine learning
            </p>
          </div>
        </div>

        {/* User controls */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex flex-col items-end">
            <span className="text-sm font-medium text-foreground leading-none">
              {user?.name}
            </span>
            <span className="text-xs text-muted-foreground mt-0.5">
              {user?.email}
            </span>
          </div>
          <Avatar className="w-9 h-9 border border-border">
            <AvatarImage src={user?.image ?? undefined} alt={user?.name ?? "User"} />
            <AvatarFallback className="text-xs font-semibold bg-primary text-primary-foreground">
              {initials}
            </AvatarFallback>
          </Avatar>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSignOut}
            disabled={signingOut}
            className="text-xs h-8"
          >
            {signingOut ? "Signing out..." : "Sign out"}
          </Button>
        </div>
      </div>
    </header>
  )
}
