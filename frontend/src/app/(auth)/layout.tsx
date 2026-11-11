import React from "react"
import { ShieldCheck } from "lucide-react"

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-between p-6">
      <div className="flex items-center space-x-2 text-slate-200">
        <ShieldCheck className="w-6 h-6 text-blue-500" />
        <span className="font-bold tracking-tight text-lg">SystemaOps</span>
      </div>

      <div className="flex-1 flex items-center justify-center my-8">
        {children}
      </div>

      <footer className="text-center text-xs text-slate-600 max-w-xl mx-auto space-y-1">
        <p>SystemaOps AI Compliance Platform is an enterprise governance and evidence orchestration engine.</p>
        <p className="text-[10px] text-slate-500">Notice: SystemaOps assists in compliance workflows but does not provide legal representation or legal certification under EU AI Act.</p>
      </footer>
    </div>
  )
}
