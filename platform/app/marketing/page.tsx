"use client";

import { Megaphone, Target, Users, BarChart3, DollarSign, Zap, CheckCircle2, Play, TrendingUp, PieChart } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const DELIVERABLES = [
  { title: "Competitor Analysis", items: ["Strengths & weaknesses", "Marketing channels used", "Market share estimates", "Opportunity gaps"], color: "#ef4444" },
  { title: "Audience Segments", items: ["3-5 detailed personas", "Demographics + psychographics", "Pain points & triggers", "Preferred channels"], color: "#3b82f6" },
  { title: "Marketing Strategy", items: ["Positioning statement", "Channel strategy", "Content pillars", "Quick wins + long-term plays"], color: "#6366f1" },
  { title: "Campaign Plans", items: ["3 ready-to-execute campaigns", "Target segments per campaign", "Creative briefs", "A/B test ideas"], color: "#8b5cf6" },
  { title: "Budget Allocation", items: ["Channel-by-channel breakdown", "Monthly spend plan", "ROI projections (1/3/6 months)", "Testing reserve"], color: "#10b981" },
  { title: "KPI Framework", items: ["North star metric", "Primary & secondary KPIs", "Dashboard metrics", "Alert thresholds"], color: "#f59e0b" },
];

export default function MarketingPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader title="Marketing Strategist" subtitle="Competitor analysis, audience segmentation, campaigns, and budget allocation" icon={<Megaphone className="w-5 h-5" />} action={<button className="btn-primary text-sm"><Zap className="w-3.5 h-3.5" /> Generate Strategy</button>} />
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Marketing Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Industry</label><input className="input-field w-full" placeholder="Industry" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Monthly Budget</label><input className="input-field w-full" placeholder="e.g. $5,000" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Competitors</label><input className="input-field w-full" placeholder="Competitor A, B, C" /></div>
        </div>
        <div className="mt-4"><label className="text-xs text-gray-500 mb-1 block">Target Audience</label><textarea className="input-field w-full h-16 resize-none" placeholder="Describe your ideal customers, their pain points, and where they spend time online..." /></div>
      </div>
      <div>
        <h3 className="section-title mb-4"><Target className="w-4 h-4 text-nexus-400" /> What Gets Delivered</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELIVERABLES.map((d) => (
            <div key={d.title} className="card-hover p-4">
              <p className="text-sm font-semibold text-white mb-2" style={{ color: d.color }}>{d.title}</p>
              <ul className="space-y-1">{d.items.map((item) => (<li key={item} className="text-xs text-gray-400 flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{item}</li>))}</ul>
            </div>
          ))}
        </div>
      </div>
      <div className="card p-8 text-center"><Megaphone className="w-10 h-10 text-gray-600 mx-auto mb-3" /><p className="text-sm text-gray-400">No marketing strategy generated yet</p></div>
    </div>
  );
}
