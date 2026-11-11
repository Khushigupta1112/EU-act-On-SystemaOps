import React from "react"
import { Badge } from "@/components/ui/badge"
import { AISystemStatus } from "@/types/ai-system"

interface StatusBadgeProps {
  status: AISystemStatus | string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  switch (status) {
    case "ACTIVE":
    case "APPROVED":
      return <Badge variant="success">{status}</Badge>
    case "IN_REVIEW":
    case "DISCOVERED":
      return <Badge variant="warning">{status}</Badge>
    case "SUSPENDED":
    case "RETIRED":
      return <Badge variant="secondary">{status}</Badge>
    case "DRAFT":
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}
