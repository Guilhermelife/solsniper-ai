import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts'
import { format } from 'date-fns'

const API_BASE = '/api'

export default function Analytics() {
  const { data: snapshotData } = useQuery({
    queryKey: ['snapshots'],
    queryFn: async () => (await axios.get(`${API_BASE}/analytics/snapshots`)).data
  })

  const { data: insightData } = useQuery({
    queryKey: ['insights'],
    queryFn: async () => (await axios.get(`${API_BASE}/analytics/insights`)).data
  })

  const snapshots = snapshotData?.snapshots || []
  
  // Format for Recharts
  const equityData = snapshots.map((s: any) => ({
    date: format(new Date(s.date), 'MMM dd'),
    balance: s.balance,
    realized_profit: s.realized_profit
  }))

  const scoreData = Object.entries(insightData?.score_performance || {}).map(([key, val]: any) => ({
    score_range: key,
    win_rate: val.win_rate,
    avg_profit: val.avg_profit
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-white">Analytics</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equity Curve */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-6">Equity Curve (Balance)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={equityData}>
                <defs>
                  <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={value => `$${value}`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', color: '#F1F5F9' }}
                  itemStyle={{ color: '#3B82F6' }}
                />
                <Area type="monotone" dataKey="balance" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#colorBalance)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Realized Profit */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-6">Realized Profit Over Time</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={value => `$${value}`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', color: '#F1F5F9' }}
                  cursor={{ fill: '#334155', opacity: 0.4 }}
                />
                <Bar dataKey="realized_profit" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Profit by Score Range */}
        <div className="bg-surface border border-slate-700/50 rounded-xl p-5 lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-6">Performance by AI Score</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="score_range" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis yAxisId="left" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={value => `$${value}`} />
                <YAxis yAxisId="right" orientation="right" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={value => `${value}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', color: '#F1F5F9' }}
                  cursor={{ fill: '#334155', opacity: 0.4 }}
                />
                <Legend />
                <Bar yAxisId="left" name="Avg Profit (USD)" dataKey="avg_profit" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" name="Win Rate (%)" dataKey="win_rate" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
