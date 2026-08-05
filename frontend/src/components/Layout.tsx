import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Activity, 
  Radio, 
  Briefcase, 
  History, 
  LineChart, 
  ShieldCheck, 
  Settings, 
  TerminalSquare, 
  Cpu 
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const API_BASE = '/api'

const fetchHealth = async () => {
  const { data } = await axios.get(`${API_BASE}/health`)
  return data
}

const fetchBadges = async () => {
  const { data } = await axios.get(`${API_BASE}/system/badges`)
  return data
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const { data: health, isError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
  })

  const { data: badges } = useQuery({
    queryKey: ['badges'],
    queryFn: fetchBadges,
    refetchInterval: 3000, // Poll every 3 seconds
  })

  // Open Positions Badge
  let openPositionsBadge = null
  if (badges) {
    const { open_positions, max_open_positions } = badges
    let colorClass = 'bg-success/20 text-success border border-success/30'
    if (open_positions > 0) {
      if (open_positions >= max_open_positions) {
        colorClass = 'bg-danger/20 text-danger border border-danger/30 animate-pulse'
      } else if (open_positions >= max_open_positions * 0.8) {
        colorClass = 'bg-warning/20 text-warning border border-warning/30'
      } else {
        colorClass = 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
      }
    }
    openPositionsBadge = (
      <span className={cn("ml-auto text-[10px] font-bold px-2 py-0.5 rounded-md transition-colors", colorClass)}>
        {open_positions}
      </span>
    )
  }

  // Live Market Badge
  let marketBadge = null
  if (badges?.scanned_tokens > 0) {
    marketBadge = (
      <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700">
        {badges.scanned_tokens}
      </span>
    )
  }

  // Signals Badge
  let signalsBadge = null
  if (badges?.pending_signals > 0) {
    signalsBadge = (
      <span className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-400 border border-purple-500/30 animate-pulse shadow-[0_0_8px_rgba(168,85,247,0.4)]">
        {badges.pending_signals}
      </span>
    )
  }

  // Logs Badge
  let logsBadge = null
  if (badges?.error_warnings > 0) {
    logsBadge = (
      <span className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-md bg-orange-500/20 text-orange-400 border border-orange-500/30">
        {badges.error_warnings}
      </span>
    )
  }

  const navItems = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'Live Market', path: '/market', icon: Activity, badge: marketBadge },
    { name: 'Live Radar', path: '/signals/live', icon: Radio },
    { name: 'Signal History', path: '/signals/history', icon: History, badge: signalsBadge },
    { name: 'Open Positions', path: '/positions/open', icon: Briefcase, badge: openPositionsBadge },
    { name: 'Closed Positions', path: '/positions/closed', icon: History },
    { name: 'Analytics', path: '/analytics', icon: LineChart },
    { name: 'Strategy Readiness', path: '/readiness', icon: ShieldCheck },
    { name: 'Configuration', path: '/config', icon: Settings },
    { name: 'Logs', path: '/logs', icon: TerminalSquare, badge: logsBadge },
    { name: 'System', path: '/system', icon: Cpu },
  ]

  const statusColor = isError ? 'bg-danger' : (health?.status === 'ok' ? 'bg-success' : 'bg-warning')

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans text-slate-300">
      {/* Sidebar */}
      <aside className="w-64 bg-surface border-r border-slate-700/50 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-700/50">
          <div className="flex items-center gap-3 text-primary font-bold text-xl tracking-tight">
            <Radio className="w-6 h-6" />
            SolSniper <span className="text-slate-100">AI</span>
          </div>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group",
                  isActive 
                    ? "bg-primary/10 text-primary" 
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                )}
              >
                <Icon className={cn("w-5 h-5", item.badge ? "group-hover:scale-110 transition-transform" : "")} />
                {item.name}
                {item.badge}
              </NavLink>
            )
          })}
        </nav>

        {/* Global Status Footer */}
        <div className="p-4 border-t border-slate-700/50">
          <div className="flex items-center gap-3 px-3 py-2 bg-slate-900/50 rounded-lg border border-slate-700/50">
            <div className={cn("w-2.5 h-2.5 rounded-full animate-pulse", statusColor)} />
            <div className="flex-1">
              <div className="text-xs font-semibold text-slate-200">System Status</div>
              <div className="text-[10px] text-slate-400">
                {isError ? 'API Offline' : (health?.status === 'ok' ? 'Connected & Live' : 'Degraded')}
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Subtle top gradient for aesthetics */}
        <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" />
        
        <div className="flex-1 overflow-y-auto p-8 z-10">
          {children}
        </div>
      </main>
    </div>
  )
}
