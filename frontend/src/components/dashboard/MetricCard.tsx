import React from "react"
import { LucideIcon } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface MetricCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  variant?: "default" | "warning" | "danger" | "success"
}

export function MetricCard({ title, value, description, icon: Icon, variant = "default" }: MetricCardProps) {
  const getIconColor = () => {
    switch (variant) {
      case "danger":
        return "text-rose-500 bg-rose-500/10 border-rose-500/20"
      case "warning":
        return "text-amber-500 bg-amber-500/10 border-amber-500/20"
      case "success":
        return "text-emerald-500 bg-emerald-500/10 border-emerald-500/20"
      case "default":
      default:
        return "text-blue-500 bg-blue-500/10 border-blue-500/20"
    }
  }

  return (
    <Card className="bg-slate-900 border-slate-800 text-slate-100">
      <CardContent className="p-5 flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 tracking-wide uppercase">{title}</p>
          <p className="text-2xl font-bold tracking-tight text-white mt-1">{value}</p>
          {description && <p className="text-xs text-slate-500 mt-1">{description}</p>}
        </div>
        <div className={`p-3 rounded-lg border ${getIconColor()}`}>
          <Icon className="w-5 h-5" />
        </div>
      </CardContent>
    </Card>
  )
}
