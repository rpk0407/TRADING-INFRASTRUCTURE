"use client";

import { UserCheck, Zap, CheckCircle2, GitBranch, Target, Shield, Bell, Users } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const DELIVERABLES = [
  { title: "Lead Scoring Model", items: ["Demographic scoring criteria", "Behavioral signals", "Engagement tracking", "Score thresholds (hot/warm/cold)", "Actions by score range"], color: "#f59e0b" },
  { title: "Customer Journeys", items: ["5-stage journey maps", "Touchpoints per stage", "Emotional state tracking", "Automated actions at each stage", "Content needs mapping"], color: "#3b82f6" },
  { title: "Automation Sequences", items: ["New lead welcome flow", "Post-purchase nurture", "Abandoned cart recovery", "Re-engagement campaign", "Upsell detection triggers"], color: "#6366f1" },
  { title: "Sales Pipeline", items: ["Custom pipeline stages", "Entry/exit criteria", "Duration targets per stage", "Conversion rate targets", "Reporting metrics"], color: "#10b981" },
  { title: "Churn Prevention", items: ["Early warning signals", "Prevention playbooks", "Health score model", "Retention campaigns", "Escalation protocols"], color: "#ef4444" },
];

export default function CRMPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader title="CRM Automator" subtitle="Lead scoring, customer journeys, pipeline design, and churn prevention" icon={<UserCheck className="w-5 h-5" />} action={<button className="btn-primary text-sm"><Zap className="w-3.5 h-3.5" /> Generate CRM System</button>} />
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">CRM Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Sales Cycle Length</label><select className="input-field w-full"><option>Short (1-7 days)</option><option>Medium (1-4 weeks)</option><option>Long (1-6 months)</option></select></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Products/Services</label><input className="input-field w-full" placeholder="e.g. Pro Plan $99/mo, Enterprise $499/mo" /></div>
        </div>
      </div>
      <div>
        <h3 className="section-title mb-4"><GitBranch className="w-4 h-4 text-nexus-400" /> What Gets Delivered</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELIVERABLES.map((d) => (
            <div key={d.title} className="card-hover p-4">
              <p className="text-sm font-semibold mb-2" style={{ color: d.color }}>{d.title}</p>
              <ul className="space-y-1">{d.items.map((item) => (<li key={item} className="text-xs text-gray-400 flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{item}</li>))}</ul>
            </div>
          ))}
        </div>
      </div>
      <div className="card p-8 text-center"><UserCheck className="w-10 h-10 text-gray-600 mx-auto mb-3" /><p className="text-sm text-gray-400">No CRM system generated yet</p></div>
    </div>
  );
}
