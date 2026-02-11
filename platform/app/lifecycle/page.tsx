"use client";

import {
  Workflow, ArrowRight, CheckCircle2, Clock, AlertTriangle,
  Users, Zap, Globe, FileText, Megaphone, UserCheck, Search,
  Headphones, Cog, BarChart3, Shield, Rocket, Heart,
  ChevronRight, Play, Target,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { StatCard } from "@/components/ui/StatCard";
import { ProgressBar } from "@/components/ui/ProgressBar";

const LIFECYCLE_PHASES = [
  {
    id: "onboard",
    name: "Onboard",
    icon: Users,
    color: "#6366f1",
    description: "Discovery, competitor research, brand strategy",
    workflows: 3,
    agents: ["Growth Analytics", "Marketing", "SEO", "Content Engine"],
    deliverables: ["Business profile", "Competitor analysis", "Brand voice guide", "Goal framework"],
  },
  {
    id: "setup",
    name: "Setup",
    icon: Cog,
    color: "#3b82f6",
    description: "Website, content, SEO, CRM, support, automation systems",
    workflows: 6,
    agents: ["Website Builder", "Content Engine", "SEO", "CRM", "Support", "Automation"],
    deliverables: ["Full website", "Content library", "SEO foundation", "CRM pipeline", "Support chatbot", "Automation workflows"],
  },
  {
    id: "launch",
    name: "Launch",
    icon: Rocket,
    color: "#10b981",
    description: "Go-live audit, marketing campaigns, content calendar, analytics baseline",
    workflows: 4,
    agents: ["SEO", "Website Builder", "Marketing", "Content Engine", "Growth Analytics"],
    deliverables: ["Launch audit report", "Active campaigns", "Content calendar", "Analytics dashboard"],
  },
  {
    id: "grow",
    name: "Grow",
    icon: Target,
    color: "#f59e0b",
    description: "Growth analysis, SEO optimization, campaign scaling, content expansion",
    workflows: 5,
    agents: ["Growth Analytics", "SEO", "Marketing", "Content Engine", "CRM"],
    deliverables: ["Growth report", "Ranking improvements", "Optimized campaigns", "Scaled content", "Lead scoring"],
  },
  {
    id: "retain",
    name: "Retain",
    icon: Heart,
    color: "#ef4444",
    description: "Health monitoring, proactive improvements, expansion opportunities",
    workflows: 3,
    agents: ["Growth Analytics", "SEO", "Website Builder", "Content Engine", "Marketing"],
    deliverables: ["Health report", "Improvement recommendations", "Expansion plan"],
  },
];

const TEMPLATES = [
  {
    name: "Complete Company Setup",
    description: "Website + Content + SEO + CRM + Support + Automation",
    phases: 3, agents: 8, workflows: 13,
    ideal: "New companies needing everything from scratch",
    color: "#6366f1",
  },
  {
    name: "Digital Transformation",
    description: "Modernize existing business with AI-powered tools",
    phases: 3, agents: 6, workflows: 10,
    ideal: "Established companies going digital",
    color: "#3b82f6",
  },
  {
    name: "Growth Accelerator",
    description: "SEO + Marketing + Analytics + Content scaling",
    phases: 2, agents: 4, workflows: 7,
    ideal: "Companies wanting to scale fast",
    color: "#10b981",
  },
  {
    name: "Lead Generation Machine",
    description: "CRM + Marketing + SEO + Content funnel",
    phases: 3, agents: 4, workflows: 8,
    ideal: "B2B companies focused on leads",
    color: "#f59e0b",
  },
  {
    name: "E-Commerce Launch",
    description: "Online store + Product content + Marketing + Support",
    phases: 4, agents: 7, workflows: 14,
    ideal: "Businesses launching online sales",
    color: "#ef4444",
  },
  {
    name: "Brand Refresh",
    description: "New website + content + updated marketing",
    phases: 3, agents: 3, workflows: 6,
    ideal: "Companies needing a rebrand",
    color: "#8b5cf6",
  },
];

export default function LifecyclePage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Client Lifecycle Engine"
        subtitle="Fully automated client journey from onboarding to growth — every phase triggers the right agents"
        icon={<Workflow className="w-5 h-5" />}
      />

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="Active Clients" value="0" icon={<Users className="w-5 h-5" />} color="#6366f1" />
        <StatCard label="Phases Completed" value="0" icon={<CheckCircle2 className="w-5 h-5" />} color="#10b981" />
        <StatCard label="Workflows Run" value="0" icon={<Workflow className="w-5 h-5" />} color="#3b82f6" />
        <StatCard label="Avg Health Score" value="100" icon={<Heart className="w-5 h-5" />} color="#ef4444" />
        <StatCard label="Templates" value="6" icon={<Zap className="w-5 h-5" />} color="#f59e0b" />
      </div>

      {/* Lifecycle Pipeline Visual */}
      <div>
        <h3 className="section-title mb-4"><ArrowRight className="w-4 h-4 text-nexus-400" /> Lifecycle Pipeline</h3>
        <div className="card p-6">
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {LIFECYCLE_PHASES.map((phase, i) => {
              const Icon = phase.icon;
              return (
                <div key={phase.id} className="flex items-center gap-2 shrink-0">
                  <div className="w-44">
                    <div className="flex items-center gap-2 mb-2">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${phase.color}15`, color: phase.color }}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-white">{phase.name}</div>
                        <div className="text-[10px] text-gray-500">{phase.workflows} workflows</div>
                      </div>
                    </div>
                    <p className="text-[11px] text-gray-400 mb-2">{phase.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {phase.agents.slice(0, 3).map((a) => (
                        <span key={a} className="text-[9px] px-1.5 py-0.5 rounded bg-surface-2 text-gray-500">{a}</span>
                      ))}
                      {phase.agents.length > 3 && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-surface-2 text-gray-500">+{phase.agents.length - 3}</span>
                      )}
                    </div>
                  </div>
                  {i < LIFECYCLE_PHASES.length - 1 && (
                    <ChevronRight className="w-4 h-4 text-gray-600 shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Phase Details */}
      <div>
        <h3 className="section-title mb-4"><CheckCircle2 className="w-4 h-4 text-nexus-400" /> Phase Deliverables</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {LIFECYCLE_PHASES.map((phase) => {
            const Icon = phase.icon;
            return (
              <div key={phase.id} className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <div
                    className="w-7 h-7 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${phase.color}15`, color: phase.color }}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-sm font-semibold text-white">{phase.name} Phase</span>
                </div>
                <div className="space-y-1.5">
                  {phase.deliverables.map((d) => (
                    <div key={d} className="flex items-center gap-2 text-xs text-gray-400">
                      <CheckCircle2 className="w-3 h-3 text-gray-600 shrink-0" />
                      {d}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Automation Templates */}
      <div>
        <h3 className="section-title mb-4"><Zap className="w-4 h-4 text-nexus-400" /> Automation Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {TEMPLATES.map((t) => (
            <div key={t.name} className="card p-4 group hover:border-nexus-500/30 transition-all cursor-pointer">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-white">{t.name}</span>
                <Play className="w-4 h-4 text-gray-600 group-hover:text-nexus-400 transition-colors" />
              </div>
              <p className="text-[11px] text-gray-400 mb-3">{t.description}</p>
              <div className="flex items-center gap-4 text-[10px] text-gray-500 mb-2">
                <span>{t.phases} phases</span>
                <span>{t.agents} agents</span>
                <span>{t.workflows} workflows</span>
              </div>
              <div className="text-[10px] px-2 py-1 rounded bg-surface-2 text-gray-400">
                Ideal for: {t.ideal}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="card p-5 border-nexus-500/20">
        <h3 className="text-sm font-semibold text-nexus-400 mb-3">How the Lifecycle Engine Works</h3>
        <div className="text-xs text-gray-400 space-y-2">
          <p><strong className="text-white">1. Onboard:</strong> Client fills intake form. AI runs discovery analysis, competitor research, and brand strategy using Growth Analytics + Marketing + Content agents.</p>
          <p><strong className="text-white">2. Setup:</strong> Based on the intake, the system auto-triggers Website Builder, Content Engine, SEO, CRM, Support, and Automation agents — all running in parallel where possible.</p>
          <p><strong className="text-white">3. Launch:</strong> Pre-launch audit ensures everything is ready. Marketing campaigns go live, content calendar starts, analytics baseline is established.</p>
          <p><strong className="text-white">4. Grow:</strong> Continuous optimization. Growth Analytics identifies opportunities, SEO agent improves rankings, Marketing scales campaigns, Content keeps producing.</p>
          <p><strong className="text-white">5. Retain:</strong> Proactive health monitoring catches issues before clients notice. Auto-triggers improvement workflows. Identifies expansion opportunities.</p>
          <p className="mt-2 text-emerald-400 font-medium">Every phase auto-advances when deliverables are complete. Self-improving feedback loop ensures quality improves with every client.</p>
        </div>
      </div>
    </div>
  );
}
