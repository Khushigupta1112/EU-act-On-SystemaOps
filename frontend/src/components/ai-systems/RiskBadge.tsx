import React from "react"
import { Badge } from "@/components/ui/badge"
import { RiskClassification } from "@/types/ai-system"

interface RiskBadgeProps {
  risk: RiskClassification
}

export function RiskBadge({ risk }: RiskBadgeProps) {
  switch (risk) {
    case "PROHIBITED":
      return <Badge variant="destructive" className="bg-red-700 hover:bg-red-800 text-white font-mono">PROHIBITED (ART. 5)</Badge>
    case "HIGH_RISK":
      return <Badge variant="destructive" className="bg-rose-500 hover:bg-rose-600 text-white font-mono">HIGH RISK</Badge>
    case "LIMITED_TRANSPARENCY":
      return <Badge variant="warning" className="bg-amber-500/20 text-amber-500 border border-amber-500/30 font-mono">LIMITED RISK</Badge>
    case "MINIMAL_OR_NO_RISK":
      return <Badge variant="success" className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">MINIMAL RISK</Badge>
    case "NEEDS_REVIEW":
    default:
      return <Badge variant="secondary" className="font-mono">NEEDS REVIEW</Badge>
  }
}
