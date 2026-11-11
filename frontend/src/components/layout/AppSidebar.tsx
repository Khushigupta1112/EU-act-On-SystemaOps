"use client"

import React, { useState } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/stores/auth"
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Cpu, 
  FileCheck2, 
  History, 
  Settings, 
  LogOut,
  Building2
} from "lucide-react"

export function AppSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, currentOrg, logout } = useAuthStore()
  const orgSlug = currentOrg?.slug || "default-org"

  const navItems = [
    { label: "Dashboard", href: `/${orgSlug}`, icon: LayoutDashboard },
    { label: "AI Registry", href: `/${orgSlug}/ai-systems`, icon: Cpu },
    { label: "Audit Trail", href: `/${orgSlug}/audit`, icon: History },
    { label: "Settings", href: `/${orgSlug}/settings`, icon: Settings },
  ]

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col h-screen text-slate-200">
      {/* Brand header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="p-1.5 rounded-lg bg-blue-600 text-white">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold tracking-tight text-white leading-none text-base">SystemaOps</h1>
          <p className="text-[10px] text-slate-400 uppercase tracking-widest mt-1 font-semibold">AI Governance</p>
        </div>
      </div>

      {/* Organization Badge */}
      <div className="px-4 py-3 mx-3 my-3 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center space-x-2.5">
        <Building2 className="w-4 h-4 text-blue-400" />
        <div className="overflow-hidden">
          <p className="text-xs font-semibold text-slate-200 truncate">{currentOrg?.name || "Workspace"}</p>
          <p className="text-[10px] text-slate-500 truncate capitalize">{currentOrg?.plan || "Enterprise"} Plan</p>
        </div>
      </div>

      {/* Nav list */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        <p className="px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Platform Control</p>
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || (item.href !== `/${orgSlug}` && pathname.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? "bg-blue-600/10 text-blue-400 border border-blue-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* User profile & Logout */}
      <div className="p-3 border-t border-slate-800 bg-slate-950">
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800">
          <div className="truncate mr-2">
            <p className="text-xs font-medium text-slate-200 truncate">{user?.full_name || user?.email || "User"}</p>
            <p className="text-[10px] text-slate-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-md transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
