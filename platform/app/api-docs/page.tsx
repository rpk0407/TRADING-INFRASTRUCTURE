"use client";

import { BookOpen, Code, Globe, Terminal, Copy, CheckCircle2 } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const ENDPOINTS = [
  { method: "GET", path: "/health", desc: "System health check", auth: false },
  { method: "GET", path: "/health/detailed", desc: "Detailed health with agent/LLM stats", auth: false },
  { method: "POST", path: "/api/v1/workflows/", desc: "Create and launch a new workflow", auth: true },
  { method: "GET", path: "/api/v1/workflows/{id}", desc: "Get workflow status and results", auth: true },
  { method: "GET", path: "/api/v1/workflows/", desc: "List all active workflows", auth: true },
  { method: "GET", path: "/api/v1/workflows/templates/all", desc: "Get pre-built workflow templates", auth: false },
  { method: "GET", path: "/api/v1/agents/", desc: "List all agents with capabilities", auth: false },
  { method: "GET", path: "/api/v1/agents/{id}", desc: "Get agent details", auth: false },
  { method: "GET", path: "/api/v1/agents/{id}/stats", desc: "Get agent execution stats", auth: false },
  { method: "GET", path: "/api/v1/clients/{id}/dashboard", desc: "Full client dashboard data", auth: true },
  { method: "PUT", path: "/api/v1/clients/{id}/profile", desc: "Update client profile", auth: true },
  { method: "GET", path: "/api/v1/clients/{id}/workflows", desc: "Client workflow history", auth: true },
  { method: "GET", path: "/api/v1/analytics/llm-usage", desc: "LLM router usage statistics", auth: true },
  { method: "GET", path: "/api/v1/analytics/platform-stats", desc: "Platform-wide statistics", auth: true },
  { method: "GET", path: "/api/v1/analytics/cost-breakdown", desc: "Cost breakdown by provider", auth: true },
  { method: "WS", path: "/ws/workflow/{id}", desc: "Real-time workflow progress stream", auth: false },
  { method: "WS", path: "/ws/dashboard/{client_id}", desc: "Real-time client dashboard updates", auth: false },
];

const EXAMPLE_REQUEST = `curl -X POST http://localhost:8000/api/v1/workflows/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_id": "client_001",
    "workflow_type": "full_setup",
    "params": {
      "business_name": "CloudPeak Analytics",
      "industry": "SaaS",
      "description": "AI-powered analytics platform",
      "target_audience": "CTOs at mid-market companies",
      "goals": ["Launch website", "Generate leads", "Reduce churn"]
    }
  }'`;

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-emerald-500/15 text-emerald-400",
  POST: "bg-blue-500/15 text-blue-400",
  PUT: "bg-amber-500/15 text-amber-400",
  DELETE: "bg-red-500/15 text-red-400",
  WS: "bg-purple-500/15 text-purple-400",
};

export default function APIDocsPage() {
  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      <SectionHeader title="API Documentation" subtitle="REST + WebSocket endpoints for the NEXUS platform" icon={<BookOpen className="w-5 h-5" />} />

      {/* Quick Start */}
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2"><Terminal className="w-4 h-4 text-nexus-400" /> Quick Start</h3>
        <div className="bg-surface-0 rounded-lg p-4 font-mono text-xs text-gray-300 overflow-x-auto whitespace-pre">{EXAMPLE_REQUEST}</div>
      </div>

      {/* Base URL */}
      <div className="card p-4 flex items-center gap-3">
        <Globe className="w-4 h-4 text-nexus-400" />
        <span className="text-sm text-gray-400">Base URL:</span>
        <code className="text-sm font-mono text-white bg-surface-0 px-2 py-0.5 rounded">http://localhost:8000</code>
      </div>

      {/* Endpoints Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-3 text-left">
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase w-20">Method</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Endpoint</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Description</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase w-16">Auth</th>
            </tr>
          </thead>
          <tbody>
            {ENDPOINTS.map((ep, i) => (
              <tr key={i} className="border-b border-surface-3/50 hover:bg-surface-2/50">
                <td className="px-4 py-2.5">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${METHOD_COLORS[ep.method]}`}>{ep.method}</span>
                </td>
                <td className="px-4 py-2.5 font-mono text-xs text-white">{ep.path}</td>
                <td className="px-4 py-2.5 text-gray-400 text-xs">{ep.desc}</td>
                <td className="px-4 py-2.5">{ep.auth ? <span className="text-amber-400 text-xs">JWT</span> : <span className="text-gray-600 text-xs">No</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* WebSocket Info */}
      <div className="card p-5 border-purple-500/20">
        <h3 className="text-sm font-semibold text-purple-400 mb-2">WebSocket Events</h3>
        <p className="text-xs text-gray-400 mb-3">Connect to workflow streams for real-time progress updates:</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {["workflow.started", "workflow.stage", "agent.started", "agent.progress", "agent.completed", "agent.error", "workflow.completed", "workflow.error"].map((e) => (
            <code key={e} className="text-[11px] font-mono px-2 py-1 rounded bg-surface-0 text-purple-300">{e}</code>
          ))}
        </div>
      </div>
    </div>
  );
}
