"use client"

import React, { useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { useCreateAISystem } from "@/lib/hooks/useAISystems"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { DeploymentEnvironment } from "@/types/ai-system"

export default function NewAISystemPage() {
  const router = useRouter()
  const params = useParams()
  const orgSlug = (params?.orgSlug as string) || "systemaops"
  const { mutateAsync: createSystem, isPending } = useCreateAISystem(orgSlug)

  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [businessPurpose, setBusinessPurpose] = useState("")
  const [department, setDepartment] = useState("")
  const [provider, setProvider] = useState("")
  const [modelName, setModelName] = useState("")
  const [deploymentEnv, setDeploymentEnv] = useState<DeploymentEnvironment>("production")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createSystem({
        name,
        description,
        business_purpose: businessPurpose,
        department,
        provider,
        model_name: modelName,
        deployment_environment: deploymentEnv,
        data_categories: [],
      })
      router.push(`/${orgSlug}/ai-systems`)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Register AI System</h2>
        <p className="text-xs text-slate-400 mt-1">
          Catalog a machine learning model, LLM endpoint, or algorithmic pipeline into the governance ledger.
        </p>
      </div>

      <Card className="bg-slate-900 border-slate-800 text-slate-100">
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label className="text-xs text-slate-300">System Name *</Label>
              <Input
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Resume Screening Engine"
                className="bg-slate-950 border-slate-800 text-slate-100"
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs text-slate-300">Business Purpose</Label>
              <Input
                value={businessPurpose}
                onChange={(e) => setBusinessPurpose(e.target.value)}
                placeholder="e.g. Automated filtering of job candidates prior to human interview"
                className="bg-slate-950 border-slate-800 text-slate-100"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs text-slate-300">Department</Label>
                <Input
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. Human Resources"
                  className="bg-slate-950 border-slate-800 text-slate-100"
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-slate-300">Provider / Vendor</Label>
                <Input
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  placeholder="e.g. OpenAI / In-House"
                  className="bg-slate-950 border-slate-800 text-slate-100"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs text-slate-300">Model Name / Version</Label>
                <Input
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  placeholder="e.g. gpt-4o / RoBERTa-v2"
                  className="bg-slate-950 border-slate-800 text-slate-100"
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-slate-300">Deployment Environment</Label>
                <select
                  value={deploymentEnv}
                  onChange={(e) => setDeploymentEnv(e.target.value as DeploymentEnvironment)}
                  className="w-full h-10 px-3 rounded-md bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </div>
            </div>

            <p className="text-xs text-slate-400">
              Risk classification and lifecycle status are assigned during the governance review.
            </p>

            <div className="pt-4 flex items-center justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                className="border-slate-800 text-xs"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium"
              >
                {isPending ? "Registering..." : "Register System"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
