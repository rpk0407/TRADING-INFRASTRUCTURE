"use client";

import {
  Cpu, DollarSign, Zap, Activity, Shield, Server, ChevronRight,
  ArrowDown, CheckCircle2, Clock, TrendingUp, AlertTriangle,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { StatCard } from "@/components/ui/StatCard";
import { ProgressBar } from "@/components/ui/ProgressBar";

const PROVIDERS = [
  {
    name: "Kimi K2.5", type: "LOCAL", status: "online", model: "kimi-k2.5",
    color: "#10b981", costIn: 0, costOut: 0, maxTokens: "128K",
    strengths: ["Strong reasoning (GPT-4 level)", "Excellent coding", "128K context", "Vision support", "Multilingual"],
    setup: "ollama pull kimi-k2.5  OR  vllm serve moonshotai/Kimi-K2.5",
    priority: 1, usage: 0, capabilities: { reasoning: 8, coding: 8, creative: 7, analysis: 8 },
  },
  {
    name: "Ollama (Mixtral)", type: "LOCAL", status: "online", model: "mixtral:8x7b",
    color: "#3b82f6", costIn: 0, costOut: 0, maxTokens: "32K",
    strengths: ["Fast inference", "Good for drafting", "Classification", "Summarization", "Low resource usage"],
    setup: "ollama pull mixtral:8x7b",
    priority: 2, usage: 0, capabilities: { reasoning: 6, coding: 7, creative: 6, analysis: 6 },
  },
  {
    name: "Gemini 2.0 Flash", type: "FREE API", status: "online", model: "gemini-2.0-flash",
    color: "#3b82f6", costIn: 0, costOut: 0, maxTokens: "1M",
    strengths: ["FREE API tier (15 RPM)", "1M context window", "Multimodal", "Fast responses", "Google integration"],
    setup: "Set GEMINI_API_KEY in .env — free at ai.google.dev",
    priority: 3, usage: 0, capabilities: { reasoning: 8, coding: 7, creative: 7, analysis: 8 },
  },
  {
    name: "AntiGravity", type: "HYBRID", status: "standby", model: "hybrid",
    color: "#f59e0b", costIn: 0.0005, costOut: 0.001, maxTokens: "32K",
    strengths: ["Local-first with cloud fallback", "Agent coordination", "Privacy preserving", "Cost tracking"],
    setup: "pip install antigravity-ai && antigravity serve --port 9090",
    priority: 4, usage: 0, capabilities: { reasoning: 7, coding: 7, creative: 7, analysis: 7 },
  },
  {
    name: "DeepSeek R1", type: "LOCAL", status: "available", model: "deepseek-r1:32b",
    color: "#06b6d4", costIn: 0, costOut: 0, maxTokens: "64K",
    strengths: ["Chain-of-thought reasoning", "Math excellence", "Open-source", "Competitive with GPT-4"],
    setup: "ollama pull deepseek-r1:32b",
    priority: 5, usage: 0, capabilities: { reasoning: 9, coding: 8, creative: 5, analysis: 9 },
  },
  {
    name: "Groq (Llama 3.3 70B)", type: "FREE API", status: "online", model: "llama-3.3-70b-versatile",
    color: "#f97316", costIn: 0, costOut: 0, maxTokens: "128K",
    strengths: ["Ultra-fast inference (500+ tok/s)", "FREE 30 RPM", "Llama 3.3 70B", "Low latency", "OpenAI-compatible API"],
    setup: "Set GROQ_API_KEY in .env — free at console.groq.com",
    priority: 6, usage: 0, capabilities: { reasoning: 8, coding: 7, creative: 7, analysis: 8 },
  },
  {
    name: "Claude API", type: "PAID FALLBACK", status: "standby", model: "claude-sonnet-4-5",
    color: "#8b5cf6", costIn: 0.003, costOut: 0.015, maxTokens: "200K",
    strengths: ["Top-tier reasoning", "Best coding", "Longest context", "Most reliable", "Complex planning"],
    setup: "Set CLAUDE_API_KEY — budget capped at $50/mo",
    priority: 7, usage: 0, capabilities: { reasoning: 10, coding: 10, creative: 9, analysis: 10 },
  },
];

const ROUTING_RULES = [
  { task: "Classification / Tagging", routed: "Ollama (Mixtral)", reason: "Simple task, fastest local model", cost: "FREE" },
  { task: "Content Drafting", routed: "Kimi K2.5", reason: "Good creative + fast local inference", cost: "FREE" },
  { task: "Code Generation", routed: "Kimi K2.5", reason: "Strong coding, free, 128K context", cost: "FREE" },
  { task: "SEO Analysis", routed: "Kimi K2.5", reason: "Analysis + creative hybrid task", cost: "FREE" },
  { task: "Complex Planning", routed: "Gemini Flash", reason: "1M context, free API, strong reasoning", cost: "FREE" },
  { task: "Deep Reasoning", routed: "DeepSeek R1", reason: "Chain-of-thought specialist, free local", cost: "FREE" },
  { task: "Fast Summarization", routed: "Groq (Llama 3.3)", reason: "Ultra-fast inference, 500+ tok/s, free API", cost: "FREE" },
  { task: "Real-time Chat", routed: "Groq (Llama 3.3)", reason: "Lowest latency, free, great for live interactions", cost: "FREE" },
  { task: "Multi-step Strategy", routed: "Claude API", reason: "Only if all 6 free providers fail — premium fallback", cost: "$0.01-0.05" },
];

export default function LLMRouterPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Intelligent LLM Router"
        subtitle="Routes every task to the cheapest model that can handle it — 95%+ runs FREE"
        icon={<Cpu className="w-5 h-5" />}
      />

      {/* Cost Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="Total Requests" value="0" icon={<Activity className="w-5 h-5" />} color="#6366f1" />
        <StatCard label="Cache Hit Rate" value="0%" icon={<Zap className="w-5 h-5" />} color="#3b82f6" />
        <StatCard label="Monthly Spend" value="$0.00" icon={<DollarSign className="w-5 h-5" />} color="#10b981" />
        <StatCard label="Budget Left" value="$50.00" icon={<Shield className="w-5 h-5" />} color="#f59e0b" />
        <StatCard label="Free Rate" value="100%" icon={<TrendingUp className="w-5 h-5" />} color="#10b981" trend={{ value: "Target: 95%+", positive: true }} />
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
                      p.type === "FREE API" ? "bg-blue-500/15 text-blue-400" :
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
          <p><strong className="text-white">Priority 1-2 (Kimi K2.5 + Ollama):</strong> Local models handle 80%+ of all tasks. Zero cost, zero latency to external APIs. Kimi K2.5 matches GPT-4 on most benchmarks.</p>
          <p><strong className="text-white">Priority 3 (Gemini Flash):</strong> Google&apos;s free API tier gives 15 requests/min with 1M context. Perfect for tasks needing massive context windows.</p>
          <p><strong className="text-white">Priority 4-5 (AntiGravity + DeepSeek R1):</strong> Specialized fallbacks. AntiGravity for agent coordination, DeepSeek R1 for chain-of-thought reasoning.</p>
          <p><strong className="text-white">Priority 6 (Groq):</strong> Ultra-fast inference (500+ tokens/sec) with free API tier. Ideal for real-time chat and quick summarization. 30 RPM free.</p>
          <p><strong className="text-white">Priority 7 (Claude API):</strong> Nuclear option. Only used when all 6 free/local providers fail on a complex reasoning task. Budget capped at $50/month.</p>
          <p className="mt-2 text-emerald-400 font-medium">Self-improving: The feedback loop tracks quality scores per provider per task type and auto-tunes routing over time.</p>
        </div>
      </div>
    </div>
  );
}
