"use client";

import {
  Bot, Globe, FileText, Megaphone, UserCheck, Search,
  BarChart3, Headphones, Cog, Zap, Activity, DollarSign,
  Layers, ArrowUpRight, Play, Settings, CheckCircle2,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { ProgressBar } from "@/components/ui/ProgressBar";

const AGENTS = [
  {
    id: "website_builder", name: "Website Builder", icon: Globe, color: "#3b82f6", status: "ready",
    desc: "Generates complete, deployable websites from business descriptions",
    capabilities: ["Full Next.js / React generation", "Component library creation", "Responsive + mobile-first", "SEO-ready structure", "One-click deploy (Vercel/Netlify)", "CMS integration", "E-commerce support"],
    outputs: ["Complete website codebase", "package.json + configs", "Tailwind styling", "Reusable components", "Deployment-ready build"],
    costTier: 1, executions: 0, avgTime: "5-10 min",
  },
  {
    id: "content_engine", name: "Content Engine", icon: FileText, color: "#8b5cf6", status: "ready",
    desc: "AI-powered content creation at scale — blogs, emails, social, ads",
    capabilities: ["Brand voice development", "30-day content calendars", "SEO-optimized blog posts", "Email nurture sequences", "Social media content", "Google/Meta/LinkedIn ad copy", "Video scripts"],
    outputs: ["Brand voice guide", "Content calendar", "Blog articles", "Email sequences", "Social posts", "Ad copy variants"],
    costTier: 1, executions: 0, avgTime: "8-12 min",
  },
  {
    id: "marketing_agent", name: "Marketing Strategist", icon: Megaphone, color: "#ec4899", status: "ready",
    desc: "Strategic marketing automation — campaigns, segmentation, budgets",
    capabilities: ["Competitor analysis", "Audience segmentation", "Campaign planning", "A/B testing strategy", "Budget allocation", "Funnel optimization", "KPI frameworks"],
    outputs: ["Competitor report", "Audience segments", "Marketing strategy", "Campaign plans", "Budget breakdown", "KPI dashboard"],
    costTier: 1, executions: 0, avgTime: "8-12 min",
  },
  {
    id: "crm_agent", name: "CRM Automator", icon: UserCheck, color: "#f59e0b", status: "ready",
    desc: "Customer relationship management automation and pipeline design",
    capabilities: ["Lead scoring models", "Customer journey mapping", "Automation sequences", "Sales pipeline design", "Churn prevention", "Upsell detection", "Health scoring"],
    outputs: ["Lead scoring model", "Journey maps", "5+ automations", "Pipeline stages", "Churn playbooks", "Integration plan"],
    costTier: 1, executions: 0, avgTime: "6-10 min",
  },
  {
    id: "seo_agent", name: "SEO Optimizer", icon: Search, color: "#10b981", status: "ready",
    desc: "Search engine optimization — keywords, technical, on-page, links",
    capabilities: ["Keyword research (20+)", "Technical SEO audit", "On-page optimization", "Schema markup (JSON-LD)", "Link building strategy", "Local SEO", "Core Web Vitals"],
    outputs: ["Keyword matrix", "Technical checklist", "Page-by-page SEO plan", "Schema markup code", "Link strategy", "robots.txt + sitemap"],
    costTier: 1, executions: 0, avgTime: "6-10 min",
  },
  {
    id: "growth_analytics", name: "Growth Analytics", icon: BarChart3, color: "#06b6d4", status: "ready",
    desc: "Business intelligence — forecasting, market sizing, growth playbooks",
    capabilities: ["Market opportunity sizing", "Unit economics modeling", "12-month revenue forecast", "Growth experiment design", "KPI dashboard design", "Cohort analysis framework", "Competitive benchmarking"],
    outputs: ["TAM/SAM/SOM analysis", "Unit economics model", "3-scenario forecast", "5 experiments (ICE scored)", "Dashboard blueprint", "Growth playbook"],
    costTier: 2, executions: 0, avgTime: "10-15 min",
  },
  {
    id: "support_agent", name: "Support Agent", icon: Headphones, color: "#6366f1", status: "ready",
    desc: "Customer support automation — FAQ, chatbots, knowledge base",
    capabilities: ["FAQ generation", "Chatbot conversation flows", "Response templates", "Ticket routing rules", "Knowledge base structure", "CSAT optimization", "Escalation protocols"],
    outputs: ["15-20 FAQs", "Chatbot decision trees", "Template library", "Routing logic", "KB structure", "SLA definitions"],
    costTier: 1, executions: 0, avgTime: "5-8 min",
  },
  {
    id: "business_automation", name: "Business Automator", icon: Cog, color: "#ef4444", status: "ready",
    desc: "Process optimization — workflows, documents, integrations, ROI",
    capabilities: ["Process audit", "Workflow automation design", "Document templates", "Integration architecture", "Reporting automation", "ROI calculation", "Tool stack recommendation"],
    outputs: ["Process audit report", "Workflow blueprints", "Document templates", "Integration map", "Automated reports", "ROI analysis"],
    costTier: 1, executions: 0, avgTime: "8-12 min",
  },
];

export default function AgentsPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Agent Fleet"
        subtitle="8 specialized AI agents — view capabilities, outputs, and status"
        icon={<Bot className="w-5 h-5" />}
        action={
          <div className="flex gap-2">
            <button className="btn-secondary text-sm"><Settings className="w-3.5 h-3.5" /> Configure</button>
            <button className="btn-primary text-sm"><Play className="w-3.5 h-3.5" /> Run All</button>
          </div>
        }
      />

      {/* Summary strip */}
      <div className="grid grid-cols-4 gap-3">
        <div className="card flex items-center gap-3 p-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center"><CheckCircle2 className="w-4 h-4 text-emerald-400" /></div>
          <div><p className="text-lg font-bold text-white">8</p><p className="text-[10px] text-gray-500 uppercase">Agents Online</p></div>
        </div>
        <div className="card flex items-center gap-3 p-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/15 flex items-center justify-center"><Layers className="w-4 h-4 text-blue-400" /></div>
          <div><p className="text-lg font-bold text-white">53</p><p className="text-[10px] text-gray-500 uppercase">Capabilities</p></div>
        </div>
        <div className="card flex items-center gap-3 p-3">
          <div className="w-8 h-8 rounded-lg bg-purple-500/15 flex items-center justify-center"><Activity className="w-4 h-4 text-purple-400" /></div>
          <div><p className="text-lg font-bold text-white">0</p><p className="text-[10px] text-gray-500 uppercase">Total Executions</p></div>
        </div>
        <div className="card flex items-center gap-3 p-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center"><DollarSign className="w-4 h-4 text-emerald-400" /></div>
          <div><p className="text-lg font-bold text-white">$0.00</p><p className="text-[10px] text-gray-500 uppercase">Total Cost</p></div>
        </div>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {AGENTS.map((agent) => {
          const Icon = agent.icon;
          return (
            <div key={agent.id} className="agent-card p-5">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${agent.color}15` }}>
                    <Icon className="w-5 h-5" style={{ color: agent.color }} />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-white">{agent.name}</h3>
                    <p className="text-xs text-gray-500">{agent.desc}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="badge-green"><span className="status-dot active" /> Ready</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Capabilities */}
                <div>
                  <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Capabilities</p>
                  <ul className="space-y-1">
                    {agent.capabilities.map((c) => (
                      <li key={c} className="text-xs text-gray-400 flex items-start gap-1.5">
                        <Zap className="w-3 h-3 mt-0.5 shrink-0" style={{ color: agent.color }} />
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
                {/* Outputs */}
                <div>
                  <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Deliverables</p>
                  <ul className="space-y-1">
                    {agent.outputs.map((o) => (
                      <li key={o} className="text-xs text-gray-400 flex items-start gap-1.5">
                        <CheckCircle2 className="w-3 h-3 mt-0.5 text-emerald-500 shrink-0" />
                        {o}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="flex items-center gap-4 mt-4 pt-3 border-t border-surface-3 text-[11px] text-gray-500">
                <span>Cost Tier: <strong className="text-emerald-400">{agent.costTier === 1 ? "FREE (Local)" : "Low"}</strong></span>
                <span>Avg Time: <strong className="text-white">{agent.avgTime}</strong></span>
                <span>Runs: <strong className="text-white">{agent.executions}</strong></span>
                <button className="ml-auto btn-primary text-xs py-1 px-3"><Play className="w-3 h-3" /> Test Run</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
