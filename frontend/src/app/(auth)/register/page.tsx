"use client"

import React, { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/hooks/useAuth"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Building, AlertCircle } from "lucide-react"

export default function RegisterPage() {
  const router = useRouter()
  const { register } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [organizationName, setOrganizationName] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isRegistering, setIsRegistering] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsRegistering(true)
    try {
      const data = await register({
        email,
        password,
        full_name: fullName,
        organization_name: organizationName,
      })
      const orgSlug = data.membership?.organization?.slug || "systemaops"
      router.push(`/${orgSlug}`)
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "Registration failed")
    } finally {
      setIsRegistering(false)
    }
  }

  return (
    <Card className="w-full max-w-md bg-slate-900 border-slate-800 text-slate-100 shadow-xl">
      <CardHeader className="text-center pb-2">
        <div className="mx-auto mb-2 p-2.5 rounded-full bg-blue-600/10 border border-blue-500/20 w-fit">
          <Building className="w-8 h-8 text-blue-500" />
        </div>
        <CardTitle className="text-xl font-bold tracking-tight">Register Organization</CardTitle>
        <CardDescription className="text-slate-400 text-xs">
          Deploy an enterprise tenant on SystemaOps
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {error && (
            <div className="p-3 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-1">
            <Label htmlFor="orgName" className="text-xs text-slate-300">Organization / Tenant Name</Label>
            <Input
              id="orgName"
              type="text"
              required
              placeholder="e.g. Acme Financial Technologies"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100 focus:border-blue-500"
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="name" className="text-xs text-slate-300">Admin Full Name</Label>
            <Input
              id="name"
              type="text"
              required
              placeholder="Jane Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100 focus:border-blue-500"
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="email" className="text-xs text-slate-300">Work Email</Label>
            <Input
              id="email"
              type="email"
              required
              placeholder="jane.doe@acme.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100 focus:border-blue-500"
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="password" className="text-xs text-slate-300">Password</Label>
            <Input
              id="password"
              type="password"
              required
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100 focus:border-blue-500"
            />
          </div>

          <Button
            type="submit"
            disabled={isRegistering}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition-colors mt-2"
          >
            {isRegistering ? "Provisioning..." : "Create Tenant Workspace"}
          </Button>

          <div className="text-center pt-2">
            <p className="text-xs text-slate-400">
              Already have an account?{" "}
              <Link href="/login" className="text-blue-400 hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
