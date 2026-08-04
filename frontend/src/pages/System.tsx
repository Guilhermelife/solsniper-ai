import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Database, Server, Activity } from 'lucide-react'

const API_BASE = '/api'

const UsageBar = ({ label, percent, detail }: any) => (
  <div className="mb-4 last:mb-0">
    <div className="flex justify-between text-sm mb-1">
      <span className="text-slate-300 font-medium">{label}</span>
      <span className="text-slate-400">{detail}</span>
    </div>
    <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700">
      <div 
        className={`h-full transition-all duration-500 ${
          percent > 90 ? 'bg-danger' : percent > 75 ? 'bg-warning' : 'bg-primary'
        }`}
        style={{ width: `${percent}%` }}
      />
    </div>
  </div>
)

export default function System() {
  const { data: sys, isLoading } = useQuery({
    queryKey: ['system'],
    queryFn: async () => (await axios.get(`${API_BASE}/system`)).data,
    refetchInterval: 10000
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Activity className="w-6 h-6 text-primary" />
          System Telemetry
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Hardware Status */}
        <div className="lg:col-span-2 bg-surface border border-slate-700/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <Server className="w-5 h-5 text-slate-400" />
            Hardware Utilization
          </h2>
          
          {isLoading ? (
            <div className="text-slate-500">Reading sensors...</div>
          ) : (
            <div className="space-y-6">
              <UsageBar 
                label="CPU Usage" 
                percent={sys?.cpu_usage_percent || 0} 
                detail={`${sys?.cpu_usage_percent || 0}%`}
              />
              <UsageBar 
                label="RAM Usage" 
                percent={sys?.ram_usage_percent || 0} 
                detail={`${sys?.ram_used_gb || 0} GB / ${sys?.ram_total_gb || 0} GB (${sys?.ram_usage_percent || 0}%)`}
              />
              <UsageBar 
                label="Disk Storage (/)" 
                percent={sys?.disk_usage_percent || 0} 
                detail={`${sys?.disk_used_gb || 0} GB / ${sys?.disk_total_gb || 0} GB (${sys?.disk_usage_percent || 0}%)`}
              />
            </div>
          )}
        </div>

        {/* Process Map */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <Database className="w-5 h-5 text-slate-400" />
            Process Map
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-sm font-medium text-slate-200">API Gateway</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Port 8000</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-sm font-medium text-slate-200">Worker Daemon</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Background</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-sm font-medium text-slate-200">PostgreSQL</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Port 5432</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-sm font-medium text-slate-200">React Frontend</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Port 3000</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
