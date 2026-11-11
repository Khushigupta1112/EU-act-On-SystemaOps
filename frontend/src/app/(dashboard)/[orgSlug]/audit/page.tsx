"use client"

import React from "react"
import { useParams } from "next/navigation"
import { useOrganizationAuditEvents } from "@/lib/hooks/useOrganization"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { History, Shield, Terminal } from "lucide-react"

export default function AuditPage() {
  const params = useParams()
  const orgSlug = (params?.orgSlug as string) || "default-org"
  const { data, isLoading } = useOrganizationAuditEvents(orgSlug)

  const events = data?.items || []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white">Immutable Audit Ledger</h2>
        <p className="text-xs text-slate-400 mt-1">
          Cryptographically recorded, append-only log of tenant governance decisions, system modifications & authentication events.
        </p>
      </div>

      <Card className="bg-slate-900 border-slate-800 text-slate-100">
        <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-semibold flex items-center space-x-2">
            <History className="w-4 h-4 text-blue-400" />
            <span>Audit Trail Activity</span>
          </CardTitle>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            Append-Only
          </span>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading audit trail...</div>
          ) : events.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No audit events recorded for this tenant yet.
            </div>
          ) : (
            <div className="divide-y divide-slate-800/60 font-mono text-xs">
              {events.map((evt) => (
                <div key={evt.id} className="p-4 flex items-start space-x-4 hover:bg-slate-800/30 transition-colors">
                  <div className="p-1.5 rounded bg-slate-950 border border-slate-800 text-blue-400">
                    <Terminal className="w-4 h-4" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{evt.action}</span>
                      <span className="text-[10px] text-slate-500">{new Date(evt.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-slate-400 text-[11px]">
                      Actor: <span className="text-slate-300">{evt.actor_email || "System"}</span> | Resource: <span className="text-slate-300">{evt.resource_type || "N/A"}</span>
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
