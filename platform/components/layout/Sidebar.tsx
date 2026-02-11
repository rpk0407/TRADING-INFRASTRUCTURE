"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bot,
  Workflow,
  Users,
  Globe,
  FileText,
  BarChart3,
  Settings,
  Cpu,
  Megaphone,
  UserCheck,
  Search,
  Headphones,
  Cog,
  ChevronLeft,
  ChevronRight,
  Zap,
  BookOpen,
} from "lucide-react";

const NAV_SECTIONS = [
  {
    label: "COMMAND CENTER",
    items: [
      { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard", badge: null },
      { href: "/agents", icon: Bot, label: "Agent Fleet", badge: "8" },
      { href: "/workflows", icon: Workflow, label: "Workflows", badge: null },
      { href: "/clients", icon: Users, label: "Clients", badge: null },
    ],
  },
  {
    label: "AGENT STUDIOS",
    items: [
      { href: "/websites", icon: Globe, label: "Website Builder", badge: null },
      { href: "/content", icon: FileText, label: "Content Engine", badge: null },
      { href: "/marketing", icon: Megaphone, label: "Marketing", badge: null },
      { href: "/crm", icon: UserCheck, label: "CRM", badge: null },
      { href: "/seo", icon: Search, label: "SEO", badge: null },
      { href: "/support", icon: Headphones, label: "Support", badge: null },
      { href: "/automation", icon: Cog, label: "Automation", badge: null },
    ],
  },
  {
    label: "INTELLIGENCE",
    items: [
      { href: "/analytics", icon: BarChart3, label: "Growth Analytics", badge: null },
      { href: "/llm-router", icon: Cpu, label: "LLM Router", badge: "FREE" },
    ],
  },
  {
    label: "SYSTEM",
    items: [
      { href: "/settings", icon: Settings, label: "Settings", badge: null },
      { href: "/api-docs", icon: BookOpen, label: "API Docs", badge: null },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`${
        collapsed ? "w-16" : "w-64"
      } bg-surface-1 border-r border-surface-3 flex flex-col transition-all duration-300 shrink-0`}
    >
      {/* Logo */}
      <div className="h-14 flex items-center px-4 border-b border-surface-3 gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-nexus-500 to-purple-600 flex items-center justify-center shrink-0">
          <Zap className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="text-sm font-bold gradient-text">NEXUS AI</h1>
            <p className="text-[10px] text-gray-500">Agentic Platform</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            {!collapsed && (
              <p className="px-3 mb-1 text-[10px] font-semibold text-gray-600 tracking-widest">
                {section.label}
              </p>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 group ${
                      isActive
                        ? "bg-nexus-600/15 text-nexus-400 border border-nexus-500/20"
                        : "text-gray-400 hover:text-gray-200 hover:bg-surface-2"
                    }`}
                    title={collapsed ? item.label : undefined}
                  >
                    <Icon
                      className={`w-4 h-4 shrink-0 ${
                        isActive ? "text-nexus-400" : "text-gray-500 group-hover:text-gray-300"
                      }`}
                    />
                    {!collapsed && (
                      <>
                        <span className="flex-1 truncate">{item.label}</span>
                        {item.badge && (
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                              item.badge === "FREE"
                                ? "bg-emerald-500/15 text-emerald-400"
                                : "bg-surface-3 text-gray-400"
                            }`}
                          >
                            {item.badge}
                          </span>
                        )}
                      </>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="h-10 border-t border-surface-3 flex items-center justify-center text-gray-500 hover:text-gray-300 transition-colors"
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  );
}
