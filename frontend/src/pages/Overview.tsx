import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Activity, DollarSign, Percent, Zap, Server, AlertTriangle, CheckCircle2 } from 'lucide-react'

const API_BASE = '/api'

const MetricCard = ({ title, value, subvalue, icon: Icon, colorClass = "text-primary" }: any) => (
  <div className="bg-surface border border-slate-700/50 rounded-xl p-5 flex items-start justify-between shadow-sm hover:border-slate-600 transition-colors">
    <div>
      <h3 className="text-slate-400 font-medium text-sm mb-1">{title}</h3>
      <div className="text-2xl font-bold text-slate-100">{value}</div>
      {subvalue && <div className="text-xs text-slate-500 mt-1">{subvalue}</div>}
    </div>
    <div className={`p-3 rounded-lg bg-slate-800/50 ${colorClass}`}>
      <Icon className="w-5 h-5" />
    </div>
  </div>
)

const StatusPill = ({ label, status }: any) => {
  const isOk = status === 'ok' || status === true
  return (
    <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-slate-800">
      <span className="text-sm font-medium text-slate-300">{label}</span>
      <div className={`flex items-center gap-1.5 text-xs font-semibold px-2 py-1 rounded-full ${isOk ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
        {isOk ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
        {isOk ? 'Operational' : 'Down'}
      </div>
    </div>
  )
}

export default function Overview() {
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: async () => (await axios.get(`${API_BASE}/analytics/stats`)).data })
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: async () => (await axios.get(`${API_BASE}/health`)).data })
  const { data: worker } = useQuery({ queryKey: ['worker'], queryFn: async () => (await axios.get(`${API_BASE}/health/worker`)).data })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-white">System Overview</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Wallet Balance" 
          value={`$${stats?.wallet?.current_balance?.toFixed(2) || '0.00'}`} 
          subvalue={`Initial: $${stats?.wallet?.initial_balance || '0.00'}`}
          icon={DollarSign} 
        />
        <MetricCard 
          title="Total PnL" 
          value={`$${(stats?.wallet?.total_profit - stats?.wallet?.total_loss || 0).toFixed(2)}`} 
          subvalue={`Profit: $${stats?.wallet?.total_profit?.toFixed(2)} | Loss: $${stats?.wallet?.total_loss?.toFixed(2)}`}
          icon={Activity} 
          colorClass={(stats?.wallet?.total_profit - stats?.wallet?.total_loss) >= 0 ? "text-success" : "text-danger"}
        />
        <MetricCard 
          title="Win Rate" 
          value={`${stats?.wallet?.win_rate?.toFixed(1) || '0.0'}%`} 
          subvalue={`${stats?.wallet?.total_trades || 0} Total Trades`}
          icon={Percent} 
          colorClass="text-accent"
        />
        <MetricCard 
          title="Active Positions" 
          value={stats?.positions?.open || '0'} 
          subvalue={`${stats?.positions?.closed || 0} Closed Positions`}
          icon={Zap} 
          colorClass="text-warning"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-surface border border-slate-700/50 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-slate-400" />
            Infrastructure Status
          </h2>
          <div className="space-y-3">
            <StatusPill label="API Server" status={health?.status} />
            <StatusPill label="Database" status={health?.database} />
            <StatusPill label="Worker Daemon" status={worker?.status} />
            <div className="mt-4 p-3 bg-slate-900/30 rounded-lg text-sm text-slate-400 space-y-2">
              <div className="flex justify-between">
                <span>Worker Uptime:</span>
                <span className="text-slate-200">{worker?.details?.uptime_seconds ? `${Math.floor(worker.details.uptime_seconds / 60)} mins` : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Scan:</span>
                <span className="text-slate-200">{worker?.details?.last_scan_seconds_ago ? `${worker.details.last_scan_seconds_ago.toFixed(1)}s ago` : 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
