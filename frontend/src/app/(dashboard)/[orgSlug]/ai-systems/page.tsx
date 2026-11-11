"use client"

import React, { useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { useAISystems } from "@/lib/hooks/useAISystems"
import { RiskBadge } from "@/components/ai-systems/RiskBadge"
import { StatusBadge } from "@/components/common/StatusBadge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search, Cpu, ArrowUpRight } from "lucide-react"

export default function AISystemsListPage() {
  const params = useParams()
  const orgSlug = (params?.orgSlug as string) || "systemaops"
  const { data, isLoading } = useAISystems(orgSlug)
  const [search, setSearch] = useState("")

  const items = data?.items || []
  const filtered = items.filter(
    (item) =>
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      (item.department && item.department.toLowerCase().includes(search.toLowerCase())) ||
      (item.provider && item.provider.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">AI Systems Inventory</h2>
          <p className="text-xs text-slate-400 mt-1">
            Registered AI models, pipelines, and agents under compliance governance
          </p>
        </div>
        <Link href={`/${orgSlug}/ai-systems/new`}>
          <Button className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Register AI System</span>
          </Button>
        </Link>
      </div>

      <div className="flex items-center space-x-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <Input
            placeholder="Search by system name, provider..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-slate-900 border-slate-800 text-xs text-slate-200"
          />
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading AI systems registry...</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="mx-auto w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
              <Cpu className="w-5 h-5" />
            </div>
            <p className="text-sm font-semibold text-white">No AI systems found</p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Get started by registering your enterprise AI models, third-party LLM endpoints, or internal classifiers.
            </p>
            <div className="pt-2">
              <Link href={`/${orgSlug}/ai-systems/new`}>
                <Button variant="outline" className="border-slate-700 text-xs">
                  Register First AI System
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3">System Name</th>
                  <th className="px-4 py-3">Risk Tier</th>
                  <th className="px-4 py-3">Lifecycle Status</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Provider / Model</th>
                  <th className="px-4 py-3">Env</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filtered.map((system) => (
                  <tr key={system.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3">
                      <p className="font-semibold text-white">{system.name}</p>
                      <p className="text-[11px] text-slate-500 truncate max-w-xs">{system.business_purpose || "No description"}</p>
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge risk={system.risk_classification} />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={system.lifecycle_status} />
                    </td>
                    <td className="px-4 py-3 text-slate-300">{system.department || "—"}</td>
                    <td className="px-4 py-3 text-slate-300">
                      {system.provider || system.model_name ? (
                        <span>{system.provider} {system.model_name && `(${system.model_name})`}</span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3 uppercase text-[11px] font-mono text-slate-400">{system.deployment_environment || "PROD"}</td>
                    <td className="px-4 py-3 text-right">
                      <Link href={`/${orgSlug}/ai-systems/${system.id}`}>
                        <Button variant="ghost" size="sm" className="h-7 px-2 text-slate-400 hover:text-white">
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
