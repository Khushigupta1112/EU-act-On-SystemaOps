import React from "react"
import { Badge } from "@/components/ui/badge"

const COMPLIANCE_AREAS = [
  { id: 1, name: "1. AI Systems Inventory", standard: "Art. 49 & 71", status: "CONFIGURED", score: "Active" },
  { id: 2, name: "2. Risk Classification", standard: "Art. 6 & Annex III", status: "CONFIGURED", score: "Active" },
  { id: 3, name: "3. AI Literacy & Training", standard: "Art. 4", status: "READY", score: "Tracked" },
  { id: 4, name: "4. Transparency & Disclosure", standard: "Art. 50", status: "READY", score: "Tracked" },
  { id: 5, name: "5. GDPR & Data Processing", standard: "Art. 10 & GDPR", status: "READY", score: "Integrated" },
  { id: 6, name: "6. Human Oversight", standard: "Art. 14", status: "READY", score: "Designated" },
  { id: 7, name: "7. Accuracy, Robustness & Cybersecurity", standard: "Art. 15", status: "READY", score: "Verified" },
  { id: 8, name: "8. Security & Incident Management", standard: "Art. 73", status: "READY", score: "Standby" },
  { id: 9, name: "9. AI Model/Vendor Assessment", standard: "Art. 25 & 28", status: "READY", score: "Enforced" },
  { id: 10, name: "10. Technical Documentation & Logging", standard: "Art. 11 & 12", status: "CONFIGURED", score: "Append-only" },
  { id: 11, name: "11. Customer Contract Governance", standard: "Art. 26", status: "READY", score: "Audited" },
  { id: 12, name: "12. Post-Market Monitoring & Review", standard: "Art. 72", status: "READY", score: "Scheduled" },
]

export function ComplianceAreaTable() {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
      <div className="p-4 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-white">SystemaOps 12-Pillar Regulatory Checklist</h3>
        <p className="text-xs text-slate-400 mt-0.5">EU AI Act & Enterprise Compliance Baseline Alignment</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
            <tr>
              <th className="px-4 py-3">Control Domain</th>
              <th className="px-4 py-3">Regulatory Reference</th>
              <th className="px-4 py-3">Control Plane Status</th>
              <th className="px-4 py-3">Assurance Model</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-medium">
            {COMPLIANCE_AREAS.map((area) => (
              <tr key={area.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-4 py-3 text-white font-medium">{area.name}</td>
                <td className="px-4 py-3 font-mono text-slate-400">{area.standard}</td>
                <td className="px-4 py-3">
                  <Badge variant="success" className="text-[10px] uppercase tracking-wide">
                    {area.status}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-slate-400">{area.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
