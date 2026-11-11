"use client"

import React from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { useAISystems } from "@/lib/hooks/useAISystems"
import { MetricCard } from "@/components/dashboard/MetricCard"
import { ComplianceAreaTable } from "@/components/dashboard/ComplianceAreaTable"
import { Button } from "@/components/ui/button"
import { Cpu, AlertTriangle, CheckCircle2, ShieldAlert, Plus, ArrowRight } from "lucide-react"

export default function DashboardPage() {
  const params = useParams()
  const orgSlug = (params?.orgSlug as string) || "systemaops"
  const { data, isLoading } = useAISystems(orgSlug)

  const aiSystems = data?.items || []
  const totalSystems = aiSystems.length
  const highRiskCount = aiSystems.filter(s => s.risk_classification === "HIGH_RISK" || s.risk_classification === "PROHIBITED").length
  const activeCount = aiSystems.filter(s => s.lifecycle_status === "ACTIVE").length

  return (
    <div className="space-y-8">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">AI Compliance Control Plane</h2>
          <p className="text-sm text-slate-400 mt-1">
            Real-time governance telemetry, continuous risk classification & EU AI Act posture
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link href={`/${orgSlug}/ai-systems/new`}>
            <Button className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Register AI System</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total AI Systems"
          value={isLoading ? "..." : totalSystems}
          description="In Enterprise Inventory"
          icon={Cpu}
        />
        <MetricCard
          title="High/Prohibited Risk"
          value={isLoading ? "..." : highRiskCount}
          description="Subject to Annex III / Art. 5"
          icon={AlertTriangle}
          variant={highRiskCount > 0 ? "danger" : "default"}
        />
        <MetricCard
          title="Active in Production"
          value={isLoading ? "..." : activeCount}
          description="Live model instances"
          icon={CheckCircle2}
          variant="success"
        />
        <MetricCard
          title="Framework Controls"
          value="12 / 12"
          description="Pillars actively tracked"
          icon={ShieldAlert}
          variant="default"
        />
      </div>

      {/* 12-Pillar Checklist */}
      <ComplianceAreaTable />

      {/* Quick Access to Registry */}
      <div className="p-5 rounded-lg border border-slate-800 bg-slate-900/60 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-white">AI Systems Registry</h4>
          <p className="text-xs text-slate-400 mt-0.5">Manage model versions, owners, risk levels, and technical documentation</p>
        </div>
        <Link href={`/${orgSlug}/ai-systems`}>
          <Button variant="outline" className="border-slate-700 text-xs flex items-center space-x-2">
            <span>Open Inventory</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>
    </div>
  )
}
