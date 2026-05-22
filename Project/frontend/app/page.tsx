import { getServerSession } from "next-auth"
import { redirect } from "next/navigation"
import { Dashboard } from "@/components/dashboard/dashboard"
import type { Session } from "next-auth"

const DEV_SESSION: Session = {
  user: {
    name: "Dev User",
    email: "dev@example.com",
    image: null,
  },
  expires: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
}

export default async function Home() {
  const isDev = process.env.NODE_ENV === "development"

  const session = isDev ? DEV_SESSION : await getServerSession()

  if (!session) {
    redirect("/login")
  }

  return <Dashboard session={session} />
}
