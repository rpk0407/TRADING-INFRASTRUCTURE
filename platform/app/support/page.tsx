"use client";

import { Headphones, Zap, CheckCircle2, MessageSquare, BookOpen, Route, Clock, Star } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const DELIVERABLES = [
  { title: "FAQ Generation", items: ["15-20 industry-relevant FAQs", "Categorized by topic", "SEO-optimized answers", "Schema markup included"], color: "#6366f1" },
  { title: "Chatbot Flows", items: ["Welcome + greeting flow", "Product inquiry flow", "Support request routing", "Appointment booking", "Fallback handling"], color: "#3b82f6" },
  { title: "Response Templates", items: ["Positive review replies", "Negative review responses", "Common issue resolutions", "Escalation templates", "Follow-up sequences"], color: "#10b981" },
  { title: "Knowledge Base", items: ["Article structure", "Category hierarchy", "Search optimization", "Version control plan"], color: "#8b5cf6" },
  { title: "Ticket Routing", items: ["Priority classification", "Department routing rules", "SLA definitions", "Escalation triggers", "Auto-assignment logic"], color: "#f59e0b" },
  { title: "CSAT Optimization", items: ["Survey design", "NPS implementation", "Feedback analysis framework", "Improvement action plans"], color: "#ec4899" },
];

export default function SupportPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader title="Support Agent" subtitle="FAQ generation, chatbot flows, knowledge base, and ticket routing automation" icon={<Headphones className="w-5 h-5" />} action={<button className="btn-primary text-sm"><Zap className="w-3.5 h-3.5" /> Generate Support System</button>} />
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Support Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Industry</label><input className="input-field w-full" placeholder="Industry" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Products/Services</label><input className="input-field w-full" placeholder="What do you sell/offer?" /></div>
        </div>
        <div className="mt-4"><label className="text-xs text-gray-500 mb-1 block">Common Customer Issues</label><textarea className="input-field w-full h-16 resize-none" placeholder="What problems do customers typically face? What questions do they ask?" /></div>
      </div>
      <div>
        <h3 className="section-title mb-4"><MessageSquare className="w-4 h-4 text-nexus-400" /> What Gets Delivered</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELIVERABLES.map((d) => (
            <div key={d.title} className="card-hover p-4">
              <p className="text-sm font-semibold mb-2" style={{ color: d.color }}>{d.title}</p>
              <ul className="space-y-1">{d.items.map((item) => (<li key={item} className="text-xs text-gray-400 flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{item}</li>))}</ul>
            </div>
          ))}
        </div>
      </div>
      <div className="card p-8 text-center"><Headphones className="w-10 h-10 text-gray-600 mx-auto mb-3" /><p className="text-sm text-gray-400">No support system generated yet</p></div>
    </div>
  );
}
