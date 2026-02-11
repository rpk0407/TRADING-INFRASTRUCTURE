"use client";

import {
  Cpu, DollarSign, Zap, Activity, Shield, Server, ChevronRight,
  ArrowDown, CheckCircle2, Clock, TrendingUp, AlertTriangle,
  Code2, Globe2, Brain, Sparkles,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { StatCard } from "@/components/ui/StatCard";
import { ProgressBar } from "@/components/ui/ProgressBar";

const PROVIDERS = [
  {
    name: "Ollama", type: "LOCAL", status: "online", model: "mixtral:8x7b / llama3.1:8b",
    color: "#10b981", costIn: 0, costOut: 0, maxTokens: "32K",
    strengths: ["Fast local inference", "Classification & tagging", "Content drafting", "Summarization", "SEO analysis", "Zero API cost"],
    setup: "ollama pull mixtral:8x7b && ollama pull llama3.1:8b",
    priority: 1, usage: 0, capabilities: { reasoning: 7, coding: 5, creative: 7, analysis: 7 },
  },
  {
    name: "OpenCode", type: "LOCAL (CODE)", status: "online", model: "deepseek-coder-v2:16b / codellama / qwen2.5-coder",
    color: "#3b82f6", costIn: 0, costOut: 0, maxTokens: "64K",
    strengths: ["Code generation specialist", "Code review & refactoring", "Code completion", "Multi-language support", "Context-aware suggestions", "Zero API cost"],
    setup: "ollama pull deepseek-coder-v2:16b && ollama pull codellama && ollama pull qwen2.5-coder",
    priority: 2, usage: 0, capabilities: { reasoning: 6, coding: 9, creative: 4, analysis: 6 },
  },
  {
    name: "OpenGravity", type: "HYBRID", status: "standby", model: "hybrid local/cloud",
    color: "#f59e0b", costIn: 0.0005, costOut: 0.001, maxTokens: "32K",
    strengths: ["Local-first with cloud fallback", "Agent coordination", "Privacy preserving", "Cost tracking", "Multi-model orchestration"],
    setup: "pip install opengravity-ai && opengravity serve --port 9090",
    priority: 3, usage: 0, capabilities: { reasoning: 7, coding: 7, creative: 7, analysis: 7 },
  },
  {
    name: "Claude", type: "PREMIUM", status: "standby", model: "claude-sonnet-4-5",
    color: "#8b5cf6", costIn: 0.003, costOut: 0.015, maxTokens: "200K",
    strengths: ["Top-tier reasoning", "Best-in-class coding", "Longest context window", "Most reliable outputs", "Complex planning & strategy"],
    setup: "Set CLAUDE_API_KEY — budget capped at $50/mo",
    priority: 4, usage: 0, capabilities: { reasoning: 10, coding: 10, creative: 9, analysis: 10 },
  },
];

const ROUTING_RULES = [
  { task: "Classification / Tagging", routed: "Ollama (Llama 3.1)", reason: "Simple task, fast local model", cost: "FREE" },
  { task: "Content Drafting", routed: "Ollama (Mixtral)", reason: "Good creative output, fast local inference", cost: "FREE" },
  { task: "Summarization", routed: "Ollama (Llama 3.1)", reason: "Efficient at extraction and compression", cost: "FREE" },
  { task: "Code Generation", routed: "OpenCode (DeepSeek Coder)", reason: "Top-tier code generation, free local model", cost: "FREE" },
  { task: "Code Review", routed: "OpenCode (Qwen2.5-Coder)", reason: "Excellent at code analysis and refactoring", cost: "FREE" },
  { task: "Code Completion", routed: "OpenCode (CodeLlama)", reason: "Fast fill-in-the-middle completions", cost: "FREE" },
  { task: "Agent Coordination", routed: "OpenGravity", reason: "Hybrid orchestration with local-first routing", cost: "~$0.001" },
  { task: "SEO Analysis", routed: "Ollama (Mixtral)", reason: "Analysis + creative hybrid task", cost: "FREE" },
  { task: "Complex Planning", routed: "Claude", reason: "Premium reasoning for multi-step strategy", cost: "$0.01-0.05" },
  { task: "Deep Reasoning", routed: "Claude", reason: "Best-in-class chain-of-thought for hard problems", cost: "$0.01-0.05" },
];

export default function LLMRouterPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Intelligent LLM Router"
        subtitle="4-provider system — routes every task to the optimal model. Local-first, premium only when needed."
        icon={<Cpu className="w-5 h-5" />}
      />

      {/* Cost Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="Total Requests" value="0" icon={<Activity className="w-5 h-5" />} color="#6366f1" />
        <StatCard label="Cache Hit Rate" value="0%" icon={<Zap className="w-5 h-5" />} color="#3b82f6" />
        <StatCard label="Monthly Spend" value="$0.00" icon={<DollarSign className="w-5 h-5" />} color="#10b981" />
        <StatCard label="Budget Left" value="$50.00" icon={<Shield className="w-5 h-5" />} color="#f59e0b" />
        <StatCard label="Free Rate" value="100%" icon={<TrendingUp className="w-5 h-5" />} color="#10b981" trend={{ value: "Target: 80%+", positive: true }} />
      </div>

      {/* Provider Cards */}
      <div>
        <h3 className="section-title mb-4"><Server className="w-4 h-4 text-nexus-400" /> LLM Providers (Priority Order)</h3>
        <div className="space-y-3">
          {PROVIDERS.map((p, i) => (
            <div key={p.name} className="card p-4">
              <div className="flex items-center gap-4">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold" style={{ backgroundColor: `${p.color}15`, color: p.color }}>
                  {p.priority}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{p.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                      p.type === "LOCAL" ? "bg-emerald-500/15 text-emerald-400" :
                      p.type === "LOCAL (CODE)" ? "bg-blue-500/15 text-blue-400" :
                      p.type === "HYBRID" ? "bg-amber-500/15 text-amber-400" :
                      "bg-purple-500/15 text-purple-400"
                    }`}>{p.type}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                      p.status === "online" ? "bg-emerald-500/15 text-emerald-400" :
                      p.status === "available" ? "bg-blue-500/15 text-blue-400" :
                      "bg-gray-500/15 text-gray-400"
                    }`}>{p.status}</span>
                  </div>
                  <p className="text-[11px] text-gray-500 mt-0.5">Model: {p.model} &middot; Context: {p.maxTokens} &middot; Cost: {p.costIn === 0 ? "FREE" : `$${p.costIn}/$${p.costOut} per 1K tokens`}</p>
                </div>
                <div className="hidden md:flex gap-6">
                  {Object.entries(p.capabilities).map(([cap, val]) => (
                    <div key={cap} className="text-center">
                      <div className="text-xs font-bold text-white">{val}/10</div>
                      <div className="text-[9px] text-gray-600 capitalize">{cap}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {p.strengths.map((s) => (
                  <span key={s} className="text-[10px] px-2 py-0.5 rounded-full bg-surface-2 text-gray-400">{s}</span>
                ))}
              </div>
              <div className="mt-2 text-[11px] text-gray-600 font-mono bg-surface-0 rounded px-2 py-1">{p.setup}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Routing Rules */}
      <div>
        <h3 className="section-title mb-4"><ArrowDown className="w-4 h-4 text-nexus-400" /> Routing Decision Table</h3>
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-3 text-left">
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Task Type</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Routed To</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Reason</th>
                <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Cost</th>
              </tr>
            </thead>
            <tbody>
              {ROUTING_RULES.map((r) => (
                <tr key={r.task} className="border-b border-surface-3/50 hover:bg-surface-2/50">
                  <td className="px-4 py-2.5 text-white font-medium">{r.task}</td>
                  <td className="px-4 py-2.5"><span className="badge-blue">{r.routed}</span></td>
                  <td className="px-4 py-2.5 text-gray-400 text-xs">{r.reason}</td>
                  <td className="px-4 py-2.5"><span className={r.cost === "FREE" ? "text-emerald-400 font-bold" : "text-amber-400"}>{r.cost}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Strategy Explanation */}
      <div className="card p-5 border-emerald-500/20">
        <h3 className="text-sm font-semibold text-emerald-400 mb-2">Cost Optimization Strategy</h3>
        <div className="text-xs text-gray-400 space-y-2">
          <p><strong className="text-white">Priority 1 — Ollama (General):</strong> Local Mixtral and Llama 3.1 models handle classification, drafting, summarization, and SEO analysis. Zero cost, zero external API calls. Covers 50%+ of all tasks.</p>
          <p><strong className="text-white">Priority 2 — OpenCode (Coding):</strong> Dedicated local coding models — DeepSeek Coder for generation, Qwen2.5-Coder for review, CodeLlama for completion. Handles all code tasks at zero cost.</p>
          <p><strong className="text-white">Priority 3 — OpenGravity (Hybrid):</strong> Local-first with cloud fallback for agent coordination and multi-model orchestration. Near-zero cost per request.</p>
          <p><strong className="text-white">Priority 4 — Claude (Premium):</strong> Reserved for complex planning and deep reasoning that local models cannot handle. Budget capped at $50/month.</p>
          <p className="mt-2 text-emerald-400 font-medium">Self-improving: The feedback loop tracks quality scores per provider per task type and auto-tunes routing over time.</p>
        </div>
      </div>
    </div>
  );
}
