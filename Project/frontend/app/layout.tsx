import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Analytics } from '@vercel/analytics/next'
import { SessionProvider } from '@/components/session-provider'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Claim Denial Prevention System',
  description: 'AI-powered healthcare claim denial prediction and prevention',
  generator: 'v0.app',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`bg-background ${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="font-sans antialiased">
        <SessionProvider>
          {children}
        </SessionProvider>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
