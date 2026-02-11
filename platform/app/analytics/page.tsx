"use client";

import { BarChart3, Zap, CheckCircle2, TrendingUp, DollarSign, Target, Beaker, PieChart, LineChart, Activity } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { StatCard } from "@/components/ui/StatCard";

const DELIVERABLES = [
  { title: "Market Analysis", items: ["TAM / SAM / SOM sizing", "Market growth rate (CAGR)", "Trend analysis (near/mid/long)", "Segment breakdown", "Competitive positioning"], color: "#06b6d4" },
  { title: "Unit Economics", items: ["ARPU / CAC / LTV modeling", "LTV:CAC ratio", "Gross margin analysis", "Payback period", "Break-even analysis", "Industry benchmarks"], color: "#3b82f6" },
  { title: "Revenue Forecast", items: ["12-month projections", "3 scenarios (conservative/moderate/aggressive)", "Monthly customer + revenue breakdown", "Key assumptions documented", "Growth milestones"], color: "#10b981" },
  { title: "Growth Experiments", items: ["5 ICE-scored experiments", "Hypothesis framework", "Sample size requirements", "Success criteria defined", "Implementation steps"], color: "#8b5cf6" },
  { title: "KPI Dashboard Design", items: ["Dashboard section layout", "Executive summary metrics", "Data source mapping", "Refresh schedules", "Access level definitions"], color: "#f59e0b" },
  { title: "Growth Playbook", items: ["Executive summary", "Immediate actions (this week)", "30-day plan (week by week)", "90-day goals", "Scaling triggers", "Resource requirements"], color: "#ec4899" },
];

export default function AnalyticsPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader title="Growth Analytics" subtitle="Revenue forecasting, market sizing, unit economics, and actionable growth playbooks" icon={<BarChart3 className="w-5 h-5" />} action={<button className="btn-primary text-sm"><Zap className="w-3.5 h-3.5" /> Run Growth Analysis</button>} />

      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Growth Analysis Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Industry</label><input className="input-field w-full" placeholder="Industry" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Current MRR</label><input className="input-field w-full" placeholder="e.g. $50,000" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Current Customers</label><input className="input-field w-full" placeholder="e.g. 120" /></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Model</label><select className="input-field w-full"><option>SaaS / Subscription</option><option>E-Commerce</option><option>Marketplace</option><option>Services / Consulting</option><option>Freemium</option></select></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Average Price</label><input className="input-field w-full" placeholder="e.g. $99/month" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Growth Strategy</label><select className="input-field w-full"><option>Organic + Paid</option><option>Product-led Growth</option><option>Sales-led</option><option>Content/SEO</option><option>Partnerships</option></select></div>
        </div>
      </div>

      {/* Forecast Preview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Market Size (TAM)" value="TBD" icon={<PieChart className="w-5 h-5" />} color="#06b6d4" />
        <StatCard label="12-Month Forecast" value="TBD" icon={<TrendingUp className="w-5 h-5" />} color="#10b981" />
        <StatCard label="LTV:CAC Ratio" value="TBD" icon={<DollarSign className="w-5 h-5" />} color="#3b82f6" />
        <StatCard label="Experiments Designed" value="5" icon={<Beaker className="w-5 h-5" />} color="#8b5cf6" />
      </div>

      <div>
        <h3 className="section-title mb-4"><TrendingUp className="w-4 h-4 text-nexus-400" /> What Gets Delivered</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELIVERABLES.map((d) => (
            <div key={d.title} className="card-hover p-4">
              <p className="text-sm font-semibold mb-2" style={{ color: d.color }}>{d.title}</p>
              <ul className="space-y-1">{d.items.map((item) => (<li key={item} className="text-xs text-gray-400 flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{item}</li>))}</ul>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-5 border-cyan-500/20">
        <h3 className="text-sm font-semibold text-cyan-400 mb-2">Why This Matters</h3>
        <p className="text-xs text-gray-400">Growth Analytics is what keeps clients coming back. By showing them their future — revenue forecasts, market opportunities, and exactly what to do next — you become indispensable. This agent turns NEXUS from a one-time tool into an ongoing growth partner.</p>
      </div>
      <div className="card p-8 text-center"><BarChart3 className="w-10 h-10 text-gray-600 mx-auto mb-3" /><p className="text-sm text-gray-400">No growth analysis generated yet</p></div>
    </div>
  );
}
