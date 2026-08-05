import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Database, Server, Activity, Cpu, Network, Clock, Zap, Target, Signal, Briefcase } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

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

const StatRow = ({ label, value, icon: Icon }: any) => (
  <div className="flex items-center justify-between py-2 border-b border-slate-700/30 last:border-0">
    <div className="flex items-center gap-2 text-slate-400 text-sm">
      {Icon && <Icon className="w-4 h-4" />}
      {label}
    </div>
    <div className="text-slate-200 font-medium font-mono text-sm">{value}</div>
  </div>
)

export default function System() {
  const [apiLatency, setApiLatency] = useState<number | null>(null)
  
  const { data: health, isLoading } = useQuery({
    queryKey: ['health-telemetry'],
    queryFn: async () => {
      const t0 = performance.now()
      const { data } = await axios.get(`${API_BASE}/health`)
      setApiLatency(performance.now() - t0)
      return data
    },
    refetchInterval: 3000
  })

  // Destructure
  const api = health?.api || {}
  const db = health?.database || {}
  const worker = health?.worker || {}

  const formatUptime = (seconds: number) => {
    if (!seconds) return '0s'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    if (h > 0) return `${h}h ${m}m`
    if (m > 0) return `${m}m ${s}s`
    return `${s}s`
  }

  const formatAge = (isoString: string) => {
    if (!isoString) return 'Never'
    try {
      return formatDistanceToNow(new Date(isoString), { addSuffix: true })
    } catch {
      return 'Unknown'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Activity className="w-6 h-6 text-primary" />
          System Telemetry
        </h1>
      </div>

      {isLoading && !health && (
        <div className="text-slate-500 animate-pulse">Establishing telemetry link...</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Database Card */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-400" />
              PostgreSQL
            </h2>
            <div className={`px-2.5 py-1 rounded-full text-xs font-bold ${
              db.status === 'Connected' ? 'bg-success/20 text-success border border-success/30' : 'bg-danger/20 text-danger border border-danger/30 animate-pulse'
            }`}>
              {db.status || 'Unknown'}
            </div>
          </div>
          
          <div className="space-y-2 flex-1">
            <StatRow label="Ping Latency" value={db.latency_ms !== undefined ? `${db.latency_ms.toFixed(1)} ms` : '-'} icon={Zap} />
            <StatRow label="Total Tables" value={db.total_tables || 'N/A'} icon={Activity} />
            <StatRow label="Database Size" value={db.size_mb ? `${db.size_mb.toFixed(2)} MB` : 'N/A'} icon={Database} />
          </div>
        </div>

        {/* Worker Daemon Card */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-orange-400" />
              Worker Daemon
            </h2>
            <div className={`px-2.5 py-1 rounded-full text-xs font-bold ${
              worker.status === 'Running' ? 'bg-success/20 text-success border border-success/30' : 'bg-danger/20 text-danger border border-danger/30 animate-pulse'
            }`}>
              {worker.status || 'Stopped'}
            </div>
          </div>

          <div className="mb-6">
            <UsageBar 
              label="CPU Usage" 
              percent={worker.cpu_usage_percent || 0} 
              detail={`${(worker.cpu_usage_percent || 0).toFixed(1)}%`}
            />
            <UsageBar 
              label="RAM Usage" 
              percent={worker.memory_usage_percent || 0} 
              detail={`${(worker.memory_usage_percent || 0).toFixed(1)}%`}
            />
          </div>
          
          <div className="space-y-2">
            <StatRow label="Last Heartbeat" value={formatAge(worker.last_heartbeat)} icon={Clock} />
            <StatRow label="Loop Duration" value={`${(worker.loop_duration_seconds || 0).toFixed(2)}s`} icon={Zap} />
            <StatRow label="Total Scans" value={worker.scans_performed?.toLocaleString() || 0} icon={Activity} />
            <StatRow label="Tokens Analyzed" value={worker.tokens_analyzed?.toLocaleString() || 0} icon={Target} />
            <StatRow label="Signals Generated" value={worker.signals_generated?.toLocaleString() || 0} icon={Signal} />
            <StatRow label="Trades Executed" value={worker.trades_executed?.toLocaleString() || 0} icon={Briefcase} />
          </div>
        </div>

        {/* API Gateway Card */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Network className="w-5 h-5 text-purple-400" />
              API Gateway
            </h2>
            <div className={`px-2.5 py-1 rounded-full text-xs font-bold ${
              api.status === 'Running' ? 'bg-success/20 text-success border border-success/30' : 'bg-danger/20 text-danger border border-danger/30 animate-pulse'
            }`}>
              {api.status || 'Unknown'}
            </div>
          </div>
          
          <div className="space-y-2 flex-1">
            <StatRow label="Uptime" value={formatUptime(api.uptime_seconds || 0)} icon={Clock} />
            <StatRow label="Request Latency" value={apiLatency !== null ? `${apiLatency.toFixed(1)} ms` : '-'} icon={Zap} />
            <StatRow label="Total Requests" value={api.total_requests?.toLocaleString() || 'N/A'} icon={Activity} />
            <StatRow label="Version" value={api.version || '-'} icon={Server} />
          </div>
        </div>
        
      </div>
    </div>
  )
}
