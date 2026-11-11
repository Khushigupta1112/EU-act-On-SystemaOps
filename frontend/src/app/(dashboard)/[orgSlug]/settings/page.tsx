"use client"

import React from "react"
import { useAuthStore } from "@/lib/stores/auth"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Settings, Shield, Building, Key } from "lucide-react"

export default function SettingsPage() {
  const { currentOrg, user } = useAuthStore()

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Tenant Settings & Governance Policy</h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure organization regulatory baselines, tenant RBAC policies & identity integrations.
        </p>
      </div>

      <div className="space-y-6">
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader className="pb-3 border-b border-slate-800">
            <CardTitle className="text-sm font-semibold flex items-center space-x-2">
              <Building className="w-4 h-4 text-blue-400" />
              <span>Organization Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-slate-400">Organization Name:</span>
                <p className="text-white font-medium mt-0.5">{currentOrg?.name || "SystemaOps Enterprise"}</p>
              </div>
              <div>
                <span className="text-slate-400">Tenant Slug:</span>
                <p className="font-mono text-slate-300 mt-0.5">{currentOrg?.slug || "systemaops"}</p>
              </div>
              <div>
                <span className="text-slate-400">Subscription Tier:</span>
                <p className="text-white font-medium mt-0.5 capitalize">{currentOrg?.plan || "Enterprise"}</p>
              </div>
              <div>
                <span className="text-slate-400">Tenant Isolation Boundary:</span>
                <p className="text-emerald-400 font-mono mt-0.5">Enforced (Row-Level & Schema)</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader className="pb-3 border-b border-slate-800">
            <CardTitle className="text-sm font-semibold flex items-center space-x-2">
              <Shield className="w-4 h-4 text-blue-400" />
              <span>Regulatory Baseline Configuration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 space-y-3 text-xs text-slate-300">
            <div className="flex items-center justify-between p-3 rounded bg-slate-950 border border-slate-800">
              <div>
                <p className="font-medium text-white">EU AI Act (Regulation (EU) 2024/1689)</p>
                <p className="text-[11px] text-slate-500">Automated classification rules and Annex III conformity triggers</p>
              </div>
              <span className="text-emerald-400 font-semibold text-[11px]">Active</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded bg-slate-950 border border-slate-800">
              <div>
                <p className="font-medium text-white">GDPR & ISO/IEC 42001 Readiness</p>
                <p className="text-[11px] text-slate-500">Continuous AI management systems data lineage review</p>
              </div>
              <span className="text-blue-400 font-semibold text-[11px]">Configured</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
