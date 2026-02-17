"use client";

import { useState } from "react";
import {
  FileText, PenTool, Mail, Share2, Megaphone, Video,
  Calendar, Mic, BookOpen, Zap, CheckCircle2, Play, Loader2, XCircle,
} from "lucide-react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { api } from "@/lib/api";

const CONTENT_TYPES = [
  { icon: PenTool, name: "Brand Voice", desc: "Tone guide, vocabulary, personality traits, writing rules", color: "#8b5cf6" },
  { icon: Calendar, name: "Content Calendar", desc: "30-day plan across all platforms with topics and schedules", color: "#3b82f6" },
  { icon: BookOpen, name: "Blog Posts", desc: "SEO-optimized articles with keywords, meta tags, and outlines", color: "#10b981" },
  { icon: Mail, name: "Email Sequences", desc: "Welcome, nurture, re-engagement, and upsell email flows", color: "#f59e0b" },
  { icon: Share2, name: "Social Media", desc: "LinkedIn, Twitter/X, Instagram posts with hashtags and timing", color: "#ec4899" },
  { icon: Megaphone, name: "Ad Copy", desc: "Google Ads, Meta Ads, LinkedIn Ads — multiple variants each", color: "#ef4444" },
  { icon: Video, name: "Video Scripts", desc: "YouTube, TikTok, and explainer video scripts", color: "#06b6d4" },
  { icon: Mic, name: "Press Releases", desc: "Professional PR templates for launches and announcements", color: "#6366f1" },
];

export default function ContentPage() {
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [form, setForm] = useState({ business_name: "", industry: "", target_audience: "", description: "" });

  async function handleGenerateStrategy() {
    if (!form.business_name) return;
    setGenerating(true);
    setResult(null);
    try {
      const res = await api.createWorkflow({
        client_id: form.business_name.toLowerCase().replace(/\s+/g, "_"),
        workflow_type: "content",
        params: {
          business_name: form.business_name,
          industry: form.industry,
          target_audience: form.target_audience,
          description: form.description,
        },
      });
      setResult({ success: true, message: `Content strategy workflow launched! ${res?.message || ""}` });
    } catch (e: any) {
      setResult({ success: false, message: e.message || "Failed — is the backend running?" });
    }
    setGenerating(false);
  }

  async function handleGenerateSingle(contentType: string) {
    if (!form.business_name) {
      setResult({ success: false, message: "Enter a business name first" });
      return;
    }
    try {
      await api.createWorkflow({
        client_id: form.business_name.toLowerCase().replace(/\s+/g, "_"),
        workflow_type: "content",
        params: {
          business_name: form.business_name,
          industry: form.industry,
          content_type: contentType,
          description: form.description,
        },
      });
      setResult({ success: true, message: `${contentType} generation started!` });
    } catch (e: any) {
      setResult({ success: false, message: e.message || "Failed" });
    }
  }

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <SectionHeader
        title="Content Engine"
        subtitle="AI-powered content creation at scale — every format, every platform"
        icon={<FileText className="w-5 h-5" />}
        action={
          <button className="btn-primary text-sm" onClick={handleGenerateStrategy} disabled={generating || !form.business_name}>
            {generating ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Generating...</> : <><Zap className="w-3.5 h-3.5" /> Generate Full Strategy</>}
          </button>
        }
      />

      {result && (
        <div className={`p-3 rounded-lg text-sm flex items-center gap-2 ${result.success ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
          {result.success ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
          {result.message}
        </div>
      )}

      {/* Config */}
      <div className="card p-5 glow-border">
        <h3 className="text-sm font-semibold text-white mb-4">Content Generation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><label className="text-xs text-gray-500 mb-1 block">Business Name</label><input className="input-field w-full" placeholder="Company name" value={form.business_name} onChange={(e) => setForm({ ...form, business_name: e.target.value })} /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Industry</label><input className="input-field w-full" placeholder="Industry" value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} /></div>
          <div><label className="text-xs text-gray-500 mb-1 block">Target Audience</label><input className="input-field w-full" placeholder="Who are you reaching?" value={form.target_audience} onChange={(e) => setForm({ ...form, target_audience: e.target.value })} /></div>
        </div>
        <div className="mt-4"><label className="text-xs text-gray-500 mb-1 block">Brand Description & Key Messages</label><textarea className="input-field w-full h-20 resize-none" placeholder="What does the brand stand for? Key differentiators, tone preferences..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
      </div>

      {/* Content Types */}
      <div>
        <h3 className="section-title mb-4"><FileText className="w-4 h-4 text-nexus-400" /> Content Types</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {CONTENT_TYPES.map((ct) => {
            const Icon = ct.icon;
            return (
              <div key={ct.name} className="card-hover p-4 cursor-pointer">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${ct.color}15` }}>
                    <Icon className="w-4 h-4" style={{ color: ct.color }} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-white">{ct.name}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-500">{ct.desc}</p>
                <button className="mt-3 btn-ghost text-xs w-full justify-center" onClick={() => handleGenerateSingle(ct.name)}><Play className="w-3 h-3" /> Generate</button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Full Strategy Output */}
      <div className="card p-5 border-purple-500/20">
        <h3 className="text-sm font-semibold text-purple-400 mb-2">Full Content Strategy Package</h3>
        <p className="text-xs text-gray-400 mb-3">When you run &quot;Generate Full Strategy&quot;, the Content Engine produces ALL of the above in one workflow:</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {["Brand Voice Guide", "30-Day Calendar", "3 Blog Posts", "5-Email Sequence", "7 Days Social Posts", "Google Ad Copy (3 variants)", "Meta Ad Copy (3 variants)", "LinkedIn Ad Copy (3 variants)"].map((item) => (
            <div key={item} className="flex items-center gap-1.5 text-xs text-gray-400">
              <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" /> {item}
            </div>
          ))}
        </div>
        <p className="text-[11px] text-gray-600 mt-3">Estimated time: 8-12 minutes &middot; Cost: $0.00 (local models)</p>
      </div>

      {/* Generated Content Placeholder */}
      <div className="card p-8 text-center">
        <FileText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
        <p className="text-sm text-gray-400">No content generated yet</p>
        <p className="text-xs text-gray-600 mt-1">Configure your brand above and generate your first content package</p>
      </div>
    </div>
  );
}
