import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"

// Add allowed emails here (comma-separated in env var, or hardcode)
const ALLOWED_EMAILS = process.env.ALLOWED_EMAILS?.split(",").map(e => e.trim().toLowerCase()) ?? []

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  pages: {
    signIn: "/login",
    error: "/login/error",
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  callbacks: {
    async signIn({ user }) {
      // If no ALLOWED_EMAILS configured, allow all (dev mode)
      if (ALLOWED_EMAILS.length === 0) return true
      
      const email = user.email?.toLowerCase()
      if (!email || !ALLOWED_EMAILS.includes(email)) {
        return false // Reject sign-in
      }
      return true
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub!
      }
      return session
    },
  },
})

export { handler as GET, handler as POST }
