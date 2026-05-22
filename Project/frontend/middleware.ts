import { withAuth } from "next-auth/middleware"

export const middleware = withAuth({
  callbacks: {
    authorized: async () => true,
  },
})

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - /login (sign-in page)
     * - /api/auth (NextAuth routes)
     * - Static files and Next.js internals
     */
    "/((?!login|api/auth|_next/static|_next/image|favicon.ico|icon.*|apple-icon.*).*)",
  ],
}
