import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCost(usd: number): string {
  if (usd === 0) return "FREE";
  if (usd < 0.01) return "<$0.01";
  return `$${usd.toFixed(2)}`;
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export const AGENT_META: Record<string, { label: string; color: string; desc: string }> = {
  website_builder: { label: "Website Builder", color: "#3b82f6", desc: "Generates full Next.js sites from business descriptions" },
  content_engine: { label: "Content Engine", color: "#8b5cf6", desc: "Blog posts, email sequences, social media, ad copy" },
  marketing_agent: { label: "Marketing Strategist", color: "#ec4899", desc: "Campaigns, audience segments, budget allocation" },
  crm_agent: { label: "CRM Automator", color: "#f59e0b", desc: "Lead scoring, customer journeys, pipeline automation" },
  seo_agent: { label: "SEO Optimizer", color: "#10b981", desc: "Keywords, technical audit, schema markup, link building" },
  growth_analytics: { label: "Growth Analytics", color: "#06b6d4", desc: "Revenue forecasting, market sizing, growth playbooks" },
  support_agent: { label: "Support Agent", color: "#6366f1", desc: "FAQ generation, chatbot flows, knowledge base" },
  business_automation: { label: "Business Automator", color: "#ef4444", desc: "Workflow design, document templates, process optimization" },
};
