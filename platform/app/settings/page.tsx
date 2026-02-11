"use client";

import { Settings, Server, Key, Globe, Bell, Shield, Users, Cpu, Database, Palette, Save } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      <SectionHeader title="Settings" subtitle="Configure LLM providers, deployment targets, and system preferences" icon={<Settings className="w-5 h-5" />} />

      {/* LLM Provider Keys */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Key className="w-4 h-4 text-nexus-400" /> LLM Provider Configuration</h3>
        <div className="space-y-4">
          <div className="p-3 bg-surface-0 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2"><span className="badge-green">LOCAL</span><span className="text-sm font-medium text-white">Kimi K2.5</span></div>
              <span className="text-xs text-emerald-400">FREE</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs text-gray-500 mb-1 block">URL</label><input className="input-field w-full text-sm" defaultValue="http://localhost:8080/v1" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">Model Name</label><input className="input-field w-full text-sm" defaultValue="kimi-k2.5" /></div>
            </div>
          </div>
          <div className="p-3 bg-surface-0 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2"><span className="badge-green">LOCAL</span><span className="text-sm font-medium text-white">Ollama</span></div>
              <span className="text-xs text-emerald-400">FREE</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div><label className="text-xs text-gray-500 mb-1 block">URL</label><input className="input-field w-full text-sm" defaultValue="http://localhost:11434" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">Default Model</label><input className="input-field w-full text-sm" defaultValue="mixtral:8x7b" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">Coding Model</label><input className="input-field w-full text-sm" defaultValue="deepseek-coder-v2:16b" /></div>
            </div>
          </div>
          <div className="p-3 bg-surface-0 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2"><span className="badge-blue">FREE API</span><span className="text-sm font-medium text-white">Gemini</span></div>
              <span className="text-xs text-emerald-400">FREE (15 RPM)</span>
            </div>
            <div><label className="text-xs text-gray-500 mb-1 block">API Key</label><input className="input-field w-full text-sm" type="password" placeholder="Get free key at ai.google.dev" /></div>
          </div>
          <div className="p-3 bg-surface-0 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2"><span className="badge-amber">HYBRID</span><span className="text-sm font-medium text-white">AntiGravity</span></div>
              <span className="text-xs text-amber-400">Near-zero</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs text-gray-500 mb-1 block">URL</label><input className="input-field w-full text-sm" defaultValue="http://localhost:9090" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">API Key</label><input className="input-field w-full text-sm" type="password" placeholder="Optional" /></div>
            </div>
          </div>
          <div className="p-3 bg-surface-0 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2"><span className="badge-purple">FALLBACK</span><span className="text-sm font-medium text-white">Claude API</span></div>
              <span className="text-xs text-purple-400">Paid (capped)</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div><label className="text-xs text-gray-500 mb-1 block">API Key</label><input className="input-field w-full text-sm" type="password" placeholder="sk-ant-..." /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">Model</label><input className="input-field w-full text-sm" defaultValue="claude-sonnet-4-5-20250929" /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">Monthly Budget ($)</label><input className="input-field w-full text-sm" defaultValue="50.00" /></div>
            </div>
          </div>
        </div>
      </div>

      {/* Deployment */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Globe className="w-4 h-4 text-nexus-400" /> Deployment Configuration</h3>
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-3">
            <div><label className="text-xs text-gray-500 mb-1 block">Default Provider</label><select className="input-field w-full text-sm"><option>Vercel</option><option>Netlify</option><option>Cloudflare Pages</option><option>Custom</option></select></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Vercel Token</label><input className="input-field w-full text-sm" type="password" placeholder="Optional" /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Netlify Token</label><input className="input-field w-full text-sm" type="password" placeholder="Optional" /></div>
          </div>
        </div>
      </div>

      {/* System */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2"><Cpu className="w-4 h-4 text-nexus-400" /> System Configuration</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div><label className="text-xs text-gray-500 mb-1 block">Environment</label><select className="input-field w-full text-sm"><option>Development</option><option>Staging</option><option>Production</option></select></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Max Concurrent Agents</label><input className="input-field w-full text-sm" defaultValue="10" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Agent Timeout (sec)</label><input className="input-field w-full text-sm" defaultValue="300" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">LLM Router Strategy</label><select className="input-field w-full text-sm"><option>Cost Optimized</option><option>Quality First</option><option>Latency Optimized</option></select></div>
        </div>
      </div>

      <div className="flex justify-end"><button className="btn-primary"><Save className="w-4 h-4" /> Save Settings</button></div>
    </div>
  );
}
