"use client";

import { Search, Zap, CheckCircle2, Globe, Code, Link, MapPin, BarChart3 } from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";

const DELIVERABLES = [
  { title: "Keyword Research", items: ["20+ keyword opportunities", "Search volume estimates", "Competition analysis", "Intent classification", "Content type mapping", "Priority ranking"], color: "#10b981" },
  { title: "Technical SEO Audit", items: ["Critical issues list", "Core Web Vitals targets", "Meta tags templates", "robots.txt + sitemap", "Page speed checklist", "Mobile optimization"], color: "#3b82f6" },
  { title: "On-Page Optimization", items: ["Page-by-page SEO plan", "Title + meta descriptions", "Heading hierarchy (H1-H6)", "Internal linking strategy", "Image alt text suggestions", "Word count targets"], color: "#6366f1" },
  { title: "Schema Markup", items: ["Organization JSON-LD", "LocalBusiness schema", "WebSite schema", "BreadcrumbList", "FAQ schema", "Product/Service schema"], color: "#8b5cf6" },
  { title: "Link Building Strategy", items: ["5+ link building methods", "Target domain types", "Linkable content ideas", "Outreach templates", "Monthly link targets"], color: "#f59e0b" },
  { title: "Local SEO", items: ["Google Business Profile", "Local citation list", "Review strategy", "Response templates", "Map pack optimization"], color: "#ef4444" },
];

export default function SEOPage() {
  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader title="SEO Optimizer" subtitle="Keyword research, technical audit, on-page optimization, schema markup, and link building" icon={<Search className="w-5 h-5" />} action={<button className="btn-primary text-sm"><Zap className="w-3.5 h-3.5" /> Run Full SEO Audit</button>} />
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">SEO Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Website URL</label><input className="input-field w-full" placeholder="https://..." /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Industry</label><input className="input-field w-full" placeholder="Industry" /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Location</label><input className="input-field w-full" placeholder="City, Country or Global" /></div>
        </div>
      </div>
      <div>
        <h3 className="section-title mb-4"><Search className="w-4 h-4 text-nexus-400" /> What Gets Delivered</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELIVERABLES.map((d) => (
            <div key={d.title} className="card-hover p-4">
              <p className="text-sm font-semibold mb-2" style={{ color: d.color }}>{d.title}</p>
              <ul className="space-y-1">{d.items.map((item) => (<li key={item} className="text-xs text-gray-400 flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />{item}</li>))}</ul>
            </div>
          ))}
        </div>
      </div>
      <div className="card p-8 text-center"><Search className="w-10 h-10 text-gray-600 mx-auto mb-3" /><p className="text-sm text-gray-400">No SEO audit generated yet</p></div>
    </div>
  );
}
