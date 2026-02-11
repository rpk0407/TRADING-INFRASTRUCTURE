"use client";

import { Cog, Zap, CheckCircle2, FileText, Link2, BarChart3, DollarSign, Clock, Workflow } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const DELIVERABLES = [
  { title: "Process Audit", items: ["Current process inventory", "Time spent analysis", "Error-prone identification", "Automation potential scoring", "Quick wins list"], color: "#ef4444" },
  { title: "Workflow Automations", items: ["Trigger-based workflows", "Multi-step sequences", "Conditional logic", "Error handling", "Integration points"], color: "#6366f1" },
  { title: "Document Templates", items: ["Invoice templates", "Proposal templates", "Contract templates", "Report templates", "Onboarding checklists"], color: "#3b82f6" },
  { title: "Integration Plan", items: ["Recommended tool stack", "Integration architecture map", "Data flow diagrams", "Implementation order", "Monthly cost estimate"], color: "#10b981" },
  { title: "Reporting Automation", items: ["Daily/weekly/monthly reports", "Executive dashboards", "Team metrics", "Client reports", "Automated delivery"], color: "#8b5cf6" },
  { title: "ROI Analysis", items: ["Hours saved monthly", "Cost savings calculation", "Implementation cost", "Payback period", "Productivity gains %"], color: "#f59e0b" },
];

export default function AutomationPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader title="Business Automator" subtitle="Process audit, workflow design, document templates, integrations, and ROI analysis" icon={<Cog className="w-5 h-5" />} action={<button className="btn-primary text-sm"><Zap className="w-3.5 h-3.5" /> Run Automation Audit</button>} />
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Automation Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Team Size</label><input className="input-field w-full" placeholder="e.g. 10" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Current Tools</label><input className="input-field w-full" placeholder="e.g. Slack, HubSpot, QuickBooks" /></div>
        </div>
        <div className="mt-4"><label className="text-xs text-gray-500 mb-1 block">Pain Points</label><textarea className="input-field w-full h-16 resize-none" placeholder="What processes are slow, manual, or error-prone? Where is time being wasted?" /></div>
      </div>
      <div>
        <h3 className="section-title mb-4"><Workflow className="w-4 h-4 text-nexus-400" /> What Gets Delivered</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELIVERABLES.map((d) => (
            <div key={d.title} className="card-hover p-4">
              <p className="text-sm font-semibold mb-2" style={{ color: d.color }}>{d.title}</p>
              <ul className="space-y-1">{d.items.map((item) => (<li key={item} className="text-xs text-gray-400 flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{item}</li>))}</ul>
            </div>
          ))}
        </div>
      </div>
      <div className="card p-8 text-center"><Cog className="w-10 h-10 text-gray-600 mx-auto mb-3" /><p className="text-sm text-gray-400">No automation audit generated yet</p></div>
    </div>
  );
}
