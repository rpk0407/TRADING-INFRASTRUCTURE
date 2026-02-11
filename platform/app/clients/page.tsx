"use client";

import { useState } from "react";
import { Users, Plus, Search, Building2, Globe, Target, Brain, ArrowUpRight, Clock, DollarSign, Workflow } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

export default function ClientsPage() {
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Client Management"
        subtitle="Onboard, manage, and track all client relationships"
        icon={<Users className="w-5 h-5" />}
        action={<button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm"><Plus className="w-3.5 h-3.5" /> New Client</button>}
      />

      {/* Onboarding Form */}
      {showForm && (
        <div className="card p-5 glow-border">
          <h3 className="text-sm font-semibold text-white mb-4">Client Onboarding</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><label className="text-xs text-gray-500 mb-1 block">Business Name *</label><input className="input-field w-full" placeholder="Company name" /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Industry *</label><input className="input-field w-full" placeholder="e.g. SaaS, E-commerce" /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Contact Email</label><input className="input-field w-full" placeholder="client@company.com" /></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div><label className="text-xs text-gray-500 mb-1 block">Business Description *</label><textarea className="input-field w-full h-24 resize-none" placeholder="What does this business do? Products, services, target market..." /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Goals & Objectives *</label><textarea className="input-field w-full h-24 resize-none" placeholder="What does the client want to achieve? Growth targets, specific needs..." /></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
            <div><label className="text-xs text-gray-500 mb-1 block">Website URL</label><input className="input-field w-full" placeholder="https://..." /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Team Size</label><input className="input-field w-full" placeholder="e.g. 10" /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Current Revenue</label><input className="input-field w-full" placeholder="e.g. $50K MRR" /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">Budget</label><input className="input-field w-full" placeholder="e.g. $5K/month" /></div>
          </div>
          <div className="mt-4 pt-4 border-t border-surface-3 flex gap-3">
            <button className="btn-primary text-sm">Create & Launch Full Setup</button>
            <button className="btn-secondary text-sm">Save Client Only</button>
            <button onClick={() => setShowForm(false)} className="btn-ghost text-sm">Cancel</button>
          </div>
        </div>
      )}

      {/* Client List Placeholder */}
      <div className="card p-10 text-center">
        <Users className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <p className="text-lg font-medium text-gray-300">No clients onboarded yet</p>
        <p className="text-sm text-gray-500 mt-2 max-w-md mx-auto">
          Add your first client above. Once onboarded, NEXUS agents will build their entire business infrastructure automatically.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3 text-xs text-gray-500">
          {["Automatic memory per client", "Cross-session learning", "Complete workflow history", "Growth tracking over time"].map((f) => (
            <span key={f} className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-surface-2"><Brain className="w-3 h-3 text-nexus-400" /> {f}</span>
          ))}
        </div>
      </div>

      {/* What happens after onboarding */}
      <div>
        <h3 className="section-title mb-4"><Target className="w-4 h-4 text-nexus-400" /> Client Lifecycle Automation</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {[
            { step: "1", title: "Onboard", desc: "Business profile, goals, brand info captured and stored in persistent memory", color: "#3b82f6" },
            { step: "2", title: "Build", desc: "Agents generate website, content, marketing, CRM, SEO — all automatically", color: "#6366f1" },
            { step: "3", title: "Optimize", desc: "Growth analytics identify opportunities, agents execute improvements", color: "#10b981" },
            { step: "4", title: "Scale", desc: "Agents learn from results, continuously improving recommendations", color: "#f59e0b" },
          ].map((s) => (
            <div key={s.step} className="card-hover p-4">
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white mb-3" style={{ backgroundColor: s.color }}>{s.step}</div>
              <p className="text-sm font-semibold text-white">{s.title}</p>
              <p className="text-xs text-gray-500 mt-1">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
