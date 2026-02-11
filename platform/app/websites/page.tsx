"use client";

import {
  Globe, Play, Code, Palette, Layout, Monitor, Smartphone,
  Tablet, Eye, Download, Upload, Rocket, Settings,
  CheckCircle2, FileCode, Layers, Zap,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const SITE_TYPES = [
  { type: "Corporate", desc: "Professional business website", pages: "5-8" },
  { type: "E-Commerce", desc: "Online store with products", pages: "8-15" },
  { type: "SaaS Landing", desc: "Product landing + pricing", pages: "4-6" },
  { type: "Portfolio", desc: "Showcase work and projects", pages: "3-5" },
  { type: "Blog/Content", desc: "Content-focused platform", pages: "4-6" },
  { type: "Custom", desc: "Define your own structure", pages: "Any" },
];

const DEPLOY_TARGETS = [
  { name: "Vercel", desc: "Best for Next.js (recommended)", status: "ready" },
  { name: "Netlify", desc: "Great for static sites", status: "ready" },
  { name: "Cloudflare Pages", desc: "Edge deployment", status: "ready" },
  { name: "Custom Server", desc: "SSH deploy to any server", status: "available" },
];

export default function WebsitesPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Website Builder Studio"
        subtitle="Generate complete, deployable websites from business descriptions"
        icon={<Globe className="w-5 h-5" />}
        action={<button className="btn-primary text-sm"><Rocket className="w-3.5 h-3.5" /> Generate Website</button>}
      />

      {/* Generation Form */}
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Website Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Industry</label><input className="input-field w-full" placeholder="e.g. SaaS, Consulting" /></div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Style</label>
            <select className="input-field w-full">
              <option>Modern Professional</option><option>Minimal Clean</option><option>Bold Creative</option><option>Classic Corporate</option><option>Startup Tech</option>
            </select>
          </div>
        </div>
        <div className="mt-4"><label className="text-xs text-gray-500 mb-1 block">Business Description</label><textarea className="input-field w-full h-20 resize-none" placeholder="Describe the business, products/services, and target audience..." /></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Primary Color</label><input type="color" className="w-full h-9 rounded-lg bg-surface-2 cursor-pointer" defaultValue="#6366f1" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Secondary Color</label><input type="color" className="w-full h-9 rounded-lg bg-surface-2 cursor-pointer" defaultValue="#1e40af" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Accent Color</label><input type="color" className="w-full h-9 rounded-lg bg-surface-2 cursor-pointer" defaultValue="#f59e0b" /></div>
        </div>
      </div>

      {/* Site Type Selection */}
      <div>
        <h3 className="section-title mb-4"><Layout className="w-4 h-4 text-nexus-400" /> Site Type</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {SITE_TYPES.map((s, i) => (
            <button key={s.type} className={`text-left p-3 rounded-xl border transition-all ${i === 0 ? "border-nexus-500/50 bg-nexus-600/10" : "border-surface-3 bg-surface-1 hover:border-surface-4"}`}>
              <p className="text-sm font-medium text-white">{s.type}</p>
              <p className="text-[11px] text-gray-500 mt-0.5">{s.desc}</p>
              <p className="text-[10px] text-gray-600 mt-1">{s.pages} pages</p>
            </button>
          ))}
        </div>
      </div>

      {/* What Gets Generated */}
      <div>
        <h3 className="section-title mb-4"><FileCode className="w-4 h-4 text-nexus-400" /> What Gets Generated</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card p-4">
            <Code className="w-5 h-5 text-blue-400 mb-2" />
            <p className="text-sm font-medium text-white">Full Codebase</p>
            <ul className="mt-2 space-y-1 text-xs text-gray-400">
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Next.js 14 + TypeScript</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Tailwind CSS styling</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Responsive components</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> SEO meta tags</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> package.json + configs</li>
            </ul>
          </div>
          <div className="card p-4">
            <Layers className="w-5 h-5 text-purple-400 mb-2" />
            <p className="text-sm font-medium text-white">Pages & Components</p>
            <ul className="mt-2 space-y-1 text-xs text-gray-400">
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Home / Landing page</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> About / Team</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Services / Products</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Contact form</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Hero, CTA, Footer, etc.</li>
            </ul>
          </div>
          <div className="card p-4">
            <Rocket className="w-5 h-5 text-amber-400 mb-2" />
            <p className="text-sm font-medium text-white">Deployment</p>
            <ul className="mt-2 space-y-1 text-xs text-gray-400">
              {DEPLOY_TARGETS.map((d) => (
                <li key={d.name} className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  {d.name} — {d.desc}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Generated Sites Placeholder */}
      <div>
        <h3 className="section-title mb-4"><Globe className="w-4 h-4 text-gray-500" /> Generated Websites</h3>
        <div className="card p-8 text-center">
          <Globe className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <p className="text-sm text-gray-400">No websites generated yet</p>
          <p className="text-xs text-gray-600 mt-1">Configure your website above and click Generate</p>
        </div>
      </div>
    </div>
  );
}
