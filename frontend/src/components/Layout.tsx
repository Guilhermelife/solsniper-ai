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

export default function Layout({ children }: { children: React.ReactNode }) {
  const { data: health, isError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
  })

  const navItems = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'Live Market', path: '/market', icon: Activity },
    { name: 'Signals', path: '/signals', icon: Radio },
    { name: 'Open Positions', path: '/positions/open', icon: Briefcase },
    { name: 'Closed Positions', path: '/positions/closed', icon: History },
    { name: 'Analytics', path: '/analytics', icon: LineChart },
    { name: 'Strategy Readiness', path: '/readiness', icon: ShieldCheck },
    { name: 'Configuration', path: '/config', icon: Settings },
    { name: 'Logs', path: '/logs', icon: TerminalSquare },
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
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive 
                    ? "bg-primary/10 text-primary" 
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                )}
              >
                <Icon className="w-5 h-5" />
                {item.name}
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
