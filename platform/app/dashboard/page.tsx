"use client";

import { useState, useEffect } from "react";
import {
  Bot, Workflow, DollarSign, Users, Zap, Globe, FileText,
  Megaphone, UserCheck, Search, BarChart3, Headphones, Cog,
  Activity, Cpu, ArrowUpRight, Clock, CheckCircle2, AlertCircle,
  TrendingUp, Server, Wifi, WifiOff,
} from "lucide-react";
import { StatCard } from "@/components/ui/StatCard";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { ProgressBar } from "@/components/ui/ProgressBar";
import Link from "next/link";
import { api } from "@/lib/api";

const AGENTS = [
  { id: "website_builder", name: "Website Builder", icon: Globe, color: "#3b82f6", status: "ready" as const, executions: 0, cost: 0 },
  { id: "content_engine", name: "Content Engine", icon: FileText, color: "#8b5cf6", status: "ready" as const, executions: 0, cost: 0 },
  { id: "marketing_agent", name: "Marketing", icon: Megaphone, color: "#ec4899", status: "ready" as const, executions: 0, cost: 0 },
  { id: "crm_agent", name: "CRM", icon: UserCheck, color: "#f59e0b", status: "ready" as const, executions: 0, cost: 0 },
  { id: "seo_agent", name: "SEO", icon: Search, color: "#10b981", status: "ready" as const, executions: 0, cost: 0 },
  { id: "growth_analytics", name: "Growth Analytics", icon: BarChart3, color: "#06b6d4", status: "ready" as const, executions: 0, cost: 0 },
  { id: "support_agent", name: "Support", icon: Headphones, color: "#6366f1", status: "ready" as const, executions: 0, cost: 0 },
  { id: "business_automation", name: "Automation", icon: Cog, color: "#ef4444", status: "ready" as const, executions: 0, cost: 0 },
];

const LLM_PROVIDERS = [
  { name: "Ollama", type: "LOCAL", status: "online", color: "#10b981", cost: "$0.00", model: "mixtral:8x7b" },
  { name: "OpenCode", type: "CODE", status: "online", color: "#3b82f6", cost: "$0.00", model: "deepseek-coder-v2" },
  { name: "OpenGravity", type: "HYBRID", status: "standby", color: "#f59e0b", cost: "$0.00", model: "hybrid" },
  { name: "Claude", type: "PREMIUM", status: "standby", color: "#8b5cf6", cost: "$0.00", model: "claude-sonnet-4-5" },
];

const WORKFLOW_TEMPLATES = [
  { name: "Full Business Setup", desc: "Website + Content + Marketing + CRM + SEO + Analytics", agents: 8, time: "15-30 min", color: "#6366f1" },
  { name: "Website Launch", desc: "Build + SEO optimize + Deploy", agents: 3, time: "10-15 min", color: "#3b82f6" },
  { name: "Growth Package", desc: "Analytics + Marketing + CRM optimization", agents: 3, time: "10-20 min", color: "#06b6d4" },
  { name: "Content Blitz", desc: "Full content strategy + calendar + assets", agents: 3, time: "10-15 min", color: "#8b5cf6" },
  { name: "Operations Overhaul", desc: "Process audit + Workflow automation", agents: 3, time: "10-15 min", color: "#ef4444" },
];

export default function DashboardPage() {
  const [backendOnline, setBackendOnline] = useState(false);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [agentList, setAgentList] = useState<any[]>([]);

  useEffect(() => {
    async function fetchLiveData() {
      try {
        const health = await api.systemHealth();
        if (health) {
          setBackendOnline(true);
          setSystemHealth(health);
        }
        const agents = await api.listAgents();
        if (agents?.agents) setAgentList(agents.agents);
      } catch {
        setBackendOnline(false);
      }
    }
    fetchLiveData();
    const interval = setInterval(fetchLiveData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const totalCost = systemHealth?.llm_router?.monthly_spend_usd ?? 0;
  const totalWorkflows = systemHealth?.active_workflows ?? 0;

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Command Center</h1>
          <p className="text-sm text-gray-500 mt-1 flex items-center gap-2">
            {backendOnline ? (
              <><Wifi className="w-3.5 h-3.5 text-emerald-400" /> Backend connected — {agentList.length || 8} agents standing by</>
            ) : (
              <><WifiOff className="w-3.5 h-3.5 text-gray-500" /> Backend offline — showing static data</>
            )}
          </p>
        </div>
        <Link href="/workflows" className="btn-primary">
          <Zap className="w-4 h-4" /> New Workflow
        </Link>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Active Agents" value={String(systemHealth?.registered_agents ?? 8)} icon={<Bot className="w-5 h-5" />} color="#6366f1" trend={{ value: backendOnline ? "All online" : "Static", positive: backendOnline }} />
        <StatCard label="Workflows Run" value={String(totalWorkflows)} icon={<Workflow className="w-5 h-5" />} color="#3b82f6" />
        <StatCard label="Total Cost" value={`$${totalCost.toFixed(2)}`} icon={<DollarSign className="w-5 h-5" />} color="#10b981" trend={{ value: "99% free", positive: true }} />
        <StatCard label="Clients" value="0" icon={<Users className="w-5 h-5" />} color="#f59e0b" />
      </div>

      {/* Main Grid: Agent Fleet + LLM Providers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Fleet */}
        <div className="lg:col-span-2">
          <SectionHeader title="Agent Fleet" subtitle="8 specialized AI agents ready to deploy" icon={<Bot className="w-5 h-5" />} action={<Link href="/agents" className="btn-ghost text-xs">View All <ArrowUpRight className="w-3 h-3" /></Link>} />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {AGENTS.map((agent) => {
              const Icon = agent.icon;
              return (
                <Link key={agent.id} href={`/agents`} className="agent-card p-4 group">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${agent.color}15` }}>
                      <Icon className="w-4 h-4" style={{ color: agent.color }} />
                    </div>
                    <div className="status-dot active" />
                  </div>
                  <p className="text-sm font-medium text-white truncate">{agent.name}</p>
                  <p className="text-[11px] text-gray-500 mt-1">{agent.executions} runs &middot; {agent.cost === 0 ? "FREE" : `$${agent.cost}`}</p>
                </Link>
              );
            })}
          </div>
        </div>

        {/* LLM Providers */}
        <div>
          <SectionHeader title="LLM Router" subtitle="Intelligent model selection" icon={<Cpu className="w-5 h-5" />} action={<Link href="/llm-router" className="btn-ghost text-xs">Details <ArrowUpRight className="w-3 h-3" /></Link>} />
          <div className="space-y-2">
            {LLM_PROVIDERS.map((p) => (
              <div key={p.name} className="card flex items-center gap-3 p-3">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: p.status === "online" ? "#10b981" : "#f59e0b" }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white">{p.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                      p.type === "LOCAL" ? "bg-emerald-500/15 text-emerald-400" :
                      p.type === "CODE" ? "bg-blue-500/15 text-blue-400" :
                      p.type === "HYBRID" ? "bg-amber-500/15 text-amber-400" :
                      "bg-purple-500/15 text-purple-400"
                    }`}>{p.type}</span>
                  </div>
                  <p className="text-[11px] text-gray-500">{p.model}</p>
                </div>
                <span className="text-xs font-medium text-emerald-400">{p.cost}</span>
              </div>
            ))}
          </div>
          <div className="card mt-3 p-3 border-emerald-500/20">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs font-medium text-emerald-400">Cost Optimization</span>
            </div>
            <p className="text-[11px] text-gray-400">90%+ of tasks run on FREE local models. Cloud APIs used only as fallback for complex reasoning.</p>
          </div>
        </div>
      </div>

      {/* Workflow Templates */}
      <div>
        <SectionHeader title="Quick Launch Workflows" subtitle="Pre-built automation packages — one click to run" icon={<Zap className="w-5 h-5" />} action={<Link href="/workflows" className="btn-ghost text-xs">Custom Builder <ArrowUpRight className="w-3 h-3" /></Link>} />
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {WORKFLOW_TEMPLATES.map((t) => (
            <div key={t.name} className="card-hover cursor-pointer group p-4">
              <div className="w-8 h-8 rounded-lg mb-3 flex items-center justify-center" style={{ backgroundColor: `${t.color}15` }}>
                <Zap className="w-4 h-4" style={{ color: t.color }} />
              </div>
              <p className="text-sm font-semibold text-white">{t.name}</p>
              <p className="text-[11px] text-gray-500 mt-1 line-clamp-2">{t.desc}</p>
              <div className="flex items-center gap-3 mt-3 text-[10px] text-gray-500">
                <span className="flex items-center gap-1"><Bot className="w-3 h-3" /> {t.agents} agents</span>
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {t.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Architecture Overview */}
      <div>
        <SectionHeader title="System Architecture" subtitle="How NEXUS processes client workflows" icon={<Server className="w-5 h-5" />} />
        <div className="card p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-center">
            {[
              { step: "1", label: "Client Request", desc: "Business description & goals", color: "#3b82f6" },
              { step: "2", label: "Orchestrator Plans", desc: "DAG-based agent selection", color: "#6366f1" },
              { step: "3", label: "Agents Execute", desc: "Parallel where possible", color: "#8b5cf6" },
              { step: "4", label: "LLM Router", desc: "Cheapest capable model", color: "#10b981" },
              { step: "5", label: "Deliverables", desc: "Website, content, strategy", color: "#f59e0b" },
            ].map((s, i) => (
              <div key={s.step} className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white mb-2" style={{ backgroundColor: s.color }}>
                  {s.step}
                </div>
                <p className="text-sm font-medium text-white">{s.label}</p>
                <p className="text-[11px] text-gray-500 mt-0.5">{s.desc}</p>
                {i < 4 && <div className="hidden md:block absolute" />}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
