"use client";

import { Bell, Search, Activity, DollarSign, Cpu, Wifi } from "lucide-react";

export function TopBar() {
  return (
    <header className="h-14 bg-surface-1 border-b border-surface-3 flex items-center justify-between px-6 shrink-0">
      {/* Search */}
      <div className="flex items-center gap-3 flex-1 max-w-md">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search agents, workflows, clients..."
            className="input-field w-full pl-9 py-1.5 text-sm"
          />
        </div>
      </div>

      {/* Live Stats */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="status-dot active" />
            <span className="text-gray-400">System Online</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <Cpu className="w-3 h-3" />
            <span>4 LLMs</span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <Activity className="w-3 h-3" />
            <span>8 Agents</span>
          </div>
          <div className="flex items-center gap-1.5 text-emerald-400">
            <DollarSign className="w-3 h-3" />
            <span>$0.00 today</span>
          </div>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-surface-2 transition-colors">
          <Bell className="w-4 h-4 text-gray-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-nexus-500 rounded-full" />
        </button>

        {/* Profile */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-nexus-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
          N
        </div>
      </div>
    </header>
  );
}
