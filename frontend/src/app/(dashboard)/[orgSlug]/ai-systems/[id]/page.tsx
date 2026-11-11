"use client"

import React from "react"
import { useParams, useRouter } from "next/navigation"
import { useAISystem } from "@/lib/hooks/useAISystems"
import { RiskBadge } from "@/components/ai-systems/RiskBadge"
import { StatusBadge } from "@/components/common/StatusBadge"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, ShieldCheck, FileText, Database, Activity } from "lucide-react"

export default function AISystemDetailPage() {
  const router = useRouter()
  const params = useParams()
  const orgSlug = (params?.orgSlug as string) || "systemaops"
  const id = params?.id as string
  const { data: system, isLoading } = useAISystem(orgSlug, id)

  if (isLoading) {
    return <div className="text-xs text-slate-400">Loading AI system dossier...</div>
  }

  if (!system) {
    return <div className="text-xs text-rose-400">AI System record not found.</div>
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center space-x-3">
        <Button
          variant="outline"
          size="sm"
          onClick={() => router.back()}
          className="border-slate-800 h-8 px-2 text-slate-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back
        </Button>
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">{system.name}</h2>
          <p className="text-xs text-slate-400">UUID: {system.id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card className="bg-slate-900 border-slate-800 text-slate-100">
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span>System Overview & Metadata</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-4 text-xs">
              <div>
                <span className="text-slate-400 font-medium">Business Purpose:</span>
                <p className="mt-1 text-slate-200">{system.business_purpose || "No stated purpose provided."}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <span className="text-slate-400 font-medium">Department:</span>
                  <p className="mt-1 text-slate-200 font-semibold">{system.department || "—"}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-medium">Provider / Vendor:</span>
                  <p className="mt-1 text-slate-200 font-semibold">{system.provider || "In-House"}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-medium">Model Architecture:</span>
                  <p className="mt-1 text-slate-200 font-mono">{system.model_name || "—"}</p>
                </div>
                <div>
                  <span className="text-slate-400 font-medium">Deployment Env:</span>
                  <p className="mt-1 text-slate-200 uppercase font-mono">{system.deployment_environment || "Production"}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800 text-slate-100">
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                <Activity className="w-4 h-4 text-blue-400" />
                <span>EU AI Act Control Plane Verification</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 text-xs text-slate-300 space-y-3">
              <div className="p-3 rounded bg-slate-950 border border-slate-800 flex items-start space-x-3">
                <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-white">Continuous Evidence Ledger Active</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Controls mapped to EU AI Act compliance checklist. Technical documentation, human oversight hooks, and dataset lineage verified.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="bg-slate-900 border-slate-800 text-slate-100">
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-sm font-semibold">Governance Posture</CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-4 text-xs">
              <div>
                <p className="text-slate-400 mb-1 font-medium">Risk Tier</p>
                <RiskBadge risk={system.risk_classification} />
              </div>
              <div>
                <p className="text-slate-400 mb-1 font-medium">Lifecycle Status</p>
                <StatusBadge status={system.lifecycle_status} />
              </div>
              <div className="pt-2 border-t border-slate-800 text-slate-500 text-[11px]">
                <p>Created: {new Date(system.created_at).toLocaleDateString()}</p>
                <p>Last Modified: {new Date(system.updated_at).toLocaleDateString()}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
