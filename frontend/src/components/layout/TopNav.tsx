"use client"

import React from "react"
import { ShieldCheck, Bell } from "lucide-react"

export function TopNav() {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/70 backdrop-blur px-6 flex items-center justify-between text-slate-200">
      <div className="flex items-center space-x-2">
        <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        <span className="text-xs text-slate-400 font-medium">Compliance Control Plane Active</span>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
          <span>EU AI Act (2024/1689)</span>
        </div>
        <button 
          aria-label="Notifications"
          className="p-2 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-900 transition-colors"
        >
          <Bell className="w-4 h-4" />
        </button>
      </div>
    </header>
  )
}
