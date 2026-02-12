"use client";

import { useState, useEffect } from "react";
import {
  Workflow, Zap, Play, Clock, Bot, CheckCircle2, AlertCircle,
  ChevronRight, Plus, ArrowUpRight, Globe, FileText, Megaphone,
  BarChart3, Cog, UserCheck, Search, Headphones, Loader2, XCircle,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { api } from "@/lib/api";

const TEMPLATES = [
  {
    id: "full_business_setup", name: "Full Business Setup", color: "#6366f1",
    desc: "Complete business infrastructure — every agent works together",
    agents: ["Website Builder", "Content Engine", "Marketing", "CRM", "SEO", "Growth Analytics", "Support", "Automation"],
    stages: [
      { label: "Stage 1", agents: ["Website Builder"], parallel: false },
      { label: "Stage 2", agents: ["Content Engine", "SEO"], parallel: true },
      { label: "Stage 3", agents: ["Marketing", "CRM"], parallel: true },
      { label: "Stage 4", agents: ["Support", "Automation"], parallel: true },
      { label: "Stage 5", agents: ["Growth Analytics"], parallel: false },
    ],
    time: "15-30 min", cost: "$0.00",
  },
  {
    id: "website_launch", name: "Website Launch", color: "#3b82f6",
    desc: "Build, optimize, and deploy a complete website",
    agents: ["Website Builder", "SEO", "Content Engine"],
    stages: [
      { label: "Stage 1", agents: ["Website Builder"], parallel: false },
      { label: "Stage 2", agents: ["SEO", "Content Engine"], parallel: true },
    ],
    time: "10-15 min", cost: "$0.00",
  },
  {
    id: "growth_package", name: "Growth Acceleration", color: "#06b6d4",
    desc: "Deep analytics + marketing strategy + CRM optimization",
    agents: ["Growth Analytics", "Marketing", "CRM"],
    stages: [
      { label: "Stage 1", agents: ["Growth Analytics"], parallel: false },
      { label: "Stage 2", agents: ["Marketing", "CRM"], parallel: true },
    ],
    time: "10-20 min", cost: "$0.00",
  },
  {
    id: "content_blitz", name: "Content Marketing Blitz", color: "#8b5cf6",
    desc: "Full content strategy with calendar and initial assets",
    agents: ["Content Engine", "SEO", "Marketing"],
    stages: [
      { label: "Stage 1", agents: ["Content Engine", "SEO"], parallel: true },
      { label: "Stage 2", agents: ["Marketing"], parallel: false },
    ],
    time: "10-15 min", cost: "$0.00",
  },
  {
    id: "operations_overhaul", name: "Operations Overhaul", color: "#ef4444",
    desc: "Process audit + workflow automation + integration planning",
    agents: ["Automation", "Support", "CRM"],
    stages: [
      { label: "Stage 1", agents: ["Automation"], parallel: false },
      { label: "Stage 2", agents: ["Support", "CRM"], parallel: true },
    ],
    time: "10-15 min", cost: "$0.00",
  },
];

export default function WorkflowsPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [launching, setLaunching] = useState(false);
  const [launchResult, setLaunchResult] = useState<any>(null);
  const [clientId, setClientId] = useState("demo_client");
  const [businessName, setBusinessName] = useState("");
  const [industry, setIndustry] = useState("");
  const [description, setDescription] = useState("");
  const [goals, setGoals] = useState("");
  const [recentWorkflows, setRecentWorkflows] = useState<any[]>([]);
  const selected = TEMPLATES.find((t) => t.id === selectedTemplate);

  useEffect(() => {
    async function loadRecent() {
      try {
        const data = await api.listWorkflows();
        if (Array.isArray(data)) setRecentWorkflows(data.slice(0, 5));
      } catch {}
    }
    loadRecent();
  }, [launchResult]);

  async function handleLaunch() {
    if (!selected) return;
    setLaunching(true);
    setLaunchResult(null);
    try {
      const result = await api.createWorkflow({
        client_id: clientId || "demo_client",
        workflow_type: selected.id,
        params: {
          business_name: businessName || "Demo Business",
          industry: industry || "Technology",
          description: description || "",
          goals: goals || "",
          template: selected.id,
        },
      });
      setLaunchResult({ success: true, data: result });
    } catch (e: any) {
      setLaunchResult({ success: false, error: e.message });
    } finally {
      setLaunching(false);
    }
  }

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Workflow Builder"
        subtitle="Launch pre-built workflows or create custom agent orchestrations"
        icon={<Workflow className="w-5 h-5" />}
        action={<button className="btn-primary text-sm"><Plus className="w-3.5 h-3.5" /> Custom Workflow</button>}
      />

      {/* Workflow Form */}
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Launch a Workflow</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Client ID</label>
            <input className="input-field w-full" placeholder="e.g. client_001" value={clientId} onChange={(e) => setClientId(e.target.value)} />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Business Name</label>
            <input className="input-field w-full" placeholder="e.g. CloudPeak Analytics" value={businessName} onChange={(e) => setBusinessName(e.target.value)} />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Industry</label>
            <input className="input-field w-full" placeholder="e.g. SaaS, E-commerce, Consulting" value={industry} onChange={(e) => setIndustry(e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Business Description</label>
            <textarea className="input-field w-full h-20 resize-none" placeholder="Describe the business, its products, and what it needs..." value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Goals</label>
            <textarea className="input-field w-full h-20 resize-none" placeholder="e.g. Launch website, generate 100 leads/month, reduce churn..." value={goals} onChange={(e) => setGoals(e.target.value)} />
          </div>
        </div>
      </div>

      {/* Template Selection */}
      <div>
        <h3 className="section-title mb-4"><Zap className="w-4 h-4 text-nexus-400" /> Workflow Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {TEMPLATES.map((t) => (
            <button
              key={t.id}
              onClick={() => setSelectedTemplate(t.id === selectedTemplate ? null : t.id)}
              className={`text-left p-4 rounded-xl border transition-all ${
                selectedTemplate === t.id
                  ? "border-nexus-500/50 bg-nexus-600/10 shadow-lg shadow-nexus-500/5"
                  : "border-surface-3 bg-surface-1 hover:border-surface-4"
              }`}
            >
              <div className="w-8 h-8 rounded-lg mb-3 flex items-center justify-center" style={{ backgroundColor: `${t.color}15` }}>
                <Zap className="w-4 h-4" style={{ color: t.color }} />
              </div>
              <p className="text-sm font-semibold text-white">{t.name}</p>
              <p className="text-[11px] text-gray-500 mt-1 line-clamp-2">{t.desc}</p>
              <div className="flex items-center gap-2 mt-3 text-[10px] text-gray-500">
                <Bot className="w-3 h-3" /> {t.agents.length} agents
                <Clock className="w-3 h-3 ml-1" /> {t.time}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Selected Template Execution Plan */}
      {selected && (
        <div className="card p-5 glow-border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="section-title"><Workflow className="w-4 h-4 text-nexus-400" /> Execution Plan: {selected.name}</h3>
            <button className="btn-primary text-sm" onClick={handleLaunch} disabled={launching}>
              {launching ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Launching...</> : <><Play className="w-3.5 h-3.5" /> Launch Workflow</>}
            </button>
          </div>

          <div className="space-y-3">
            {selected.stages.map((stage, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="w-20 shrink-0 text-xs font-medium text-gray-500">{stage.label}</div>
                <div className="flex-1 flex items-center gap-2">
                  {stage.agents.map((a) => (
                    <div key={a} className="badge-blue text-xs px-3 py-1">{a}</div>
                  ))}
                  {stage.parallel && <span className="text-[10px] text-gray-600 ml-1">(parallel)</span>}
                </div>
                <ChevronRight className="w-4 h-4 text-gray-600" />
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 mt-4 pt-3 border-t border-surface-3 text-xs text-gray-500">
            <span>Estimated time: <strong className="text-white">{selected.time}</strong></span>
            <span>Estimated cost: <strong className="text-emerald-400">{selected.cost}</strong></span>
            <span>Agents involved: <strong className="text-white">{selected.agents.length}</strong></span>
          </div>

          {launchResult && (
            <div className={`mt-4 p-3 rounded-lg text-sm flex items-center gap-2 ${
              launchResult.success ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
            }`}>
              {launchResult.success ? (
                <><CheckCircle2 className="w-4 h-4" /> Workflow launched! ID: {launchResult.data?.workflow_id || "created"}</>
              ) : (
                <><XCircle className="w-4 h-4" /> {launchResult.error || "Launch failed — is the backend running?"}</>
              )}
            </div>
          )}
        </div>
      )}

      {/* Recent Workflows */}
      <div>
        <h3 className="section-title mb-4"><Clock className="w-4 h-4 text-gray-500" /> Recent Workflows</h3>
        {recentWorkflows.length > 0 ? (
          <div className="space-y-2">
            {recentWorkflows.map((w: any, i: number) => (
              <div key={w.workflow_id || i} className="card p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Workflow className="w-4 h-4 text-nexus-400" />
                  <div>
                    <p className="text-sm text-white font-medium">{w.workflow_type || w.type || "Workflow"}</p>
                    <p className="text-[11px] text-gray-500">{w.client_id || "—"} &middot; {w.status || "unknown"}</p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  w.status === "completed" ? "bg-emerald-500/15 text-emerald-400" :
                  w.status === "running" ? "bg-blue-500/15 text-blue-400" :
                  w.status === "failed" ? "bg-red-500/15 text-red-400" :
                  "bg-gray-500/15 text-gray-400"
                }`}>{w.status || "pending"}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="card p-8 text-center">
            <Workflow className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-sm text-gray-400">No workflows executed yet</p>
            <p className="text-xs text-gray-600 mt-1">Select a template above and launch your first workflow</p>
          </div>
        )}
      </div>
    </div>
  );
}
