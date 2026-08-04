import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { X, ExternalLink, Activity, DollarSign, Droplets, Clock, AlertTriangle } from 'lucide-react'
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip as RechartsTooltip,
  CartesianGrid
} from 'recharts'
import { format } from 'date-fns'

const API_BASE = '/api'

interface TokenDetailModalProps {
  address: string
  onClose: () => void
}

export function TokenDetailModal({ address, onClose }: TokenDetailModalProps) {
  
  // Fetch detailed token info (including socials)
  const { data: token, isLoading: tokenLoading } = useQuery({
    queryKey: ['token', address],
    queryFn: async () => (await axios.get(`${API_BASE}/tokens/${address}`)).data,
  })

  // Fetch historical snapshots
  const { data: snapshots, isLoading: snapshotsLoading } = useQuery({
    queryKey: ['token_snapshots', address],
    queryFn: async () => (await axios.get(`${API_BASE}/tokens/${address}/snapshots`)).data,
  })

  const chartData = snapshots?.map((s: any) => ({
    time: format(new Date(s.timestamp), 'HH:mm'),
    price: s.price_usd,
    volume: s.volume_24h,
    fullDate: new Date(s.timestamp).toLocaleString()
  })) || []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-surface border border-slate-700/50 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700/50">
          <div className="flex items-center gap-4">
            {token?.image ? (
              <img src={token.image} alt={token?.symbol} className="w-12 h-12 rounded-full border border-slate-700 bg-slate-800" />
            ) : (
              <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xl font-bold text-slate-400">
                {token?.symbol?.charAt(0) || '?'}
              </div>
            )}
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                {token?.name || 'Loading...'}
                <span className="px-2 py-0.5 rounded text-xs font-mono bg-slate-800 text-slate-300 border border-slate-700">
                  ${token?.symbol || '...'}
                </span>
              </h2>
              <div className="text-sm text-slate-400 font-mono mt-1">{address}</div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Top Metrics Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50">
               <div className="flex items-center gap-2 text-slate-400 mb-2">
                 <DollarSign className="w-4 h-4" />
                 <span className="text-sm font-medium">Market Cap</span>
               </div>
               <div className="text-xl font-bold text-white">
                 ${Number(token?.market_cap || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
               </div>
             </div>
             
             <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50">
               <div className="flex items-center gap-2 text-slate-400 mb-2">
                 <Droplets className="w-4 h-4" />
                 <span className="text-sm font-medium">Liquidity</span>
               </div>
               <div className="text-xl font-bold text-white">
                 ${Number(token?.liquidity || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
               </div>
             </div>

             <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50">
               <div className="flex items-center gap-2 text-slate-400 mb-2">
                 <Activity className="w-4 h-4" />
                 <span className="text-sm font-medium">Volume 24h</span>
               </div>
               <div className="text-xl font-bold text-white">
                 ${Number(token?.volume_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
               </div>
             </div>

             <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50">
               <div className="flex items-center gap-2 text-slate-400 mb-2">
                 <Clock className="w-4 h-4" />
                 <span className="text-sm font-medium">Age</span>
               </div>
               <div className="text-xl font-bold text-white">
                 {token?.age_minutes ? `${Math.floor(token.age_minutes / 60)}h ${Math.floor(token.age_minutes % 60)}m` : '-'}
               </div>
             </div>
          </div>

          {/* Socials Row */}
          <div className="flex items-center flex-wrap gap-3">
            {token?.website && (
              <a href={token.website} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-slate-300 hover:text-white transition-colors">
                <ExternalLink className="w-4 h-4" /> Website
              </a>
            )}
            {token?.twitter && (
              <a href={token.twitter} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-blue-400 hover:text-blue-300 transition-colors">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
                Twitter
              </a>
            )}
            {token?.telegram && (
              <a href={token.telegram} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-sky-400 hover:text-sky-300 transition-colors">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .24z"/></svg>
                Telegram
              </a>
            )}
            {!tokenLoading && !token?.website && !token?.twitter && !token?.telegram && (
              <div className="flex items-center gap-2 text-sm text-slate-500 bg-slate-800/30 px-4 py-2 rounded-lg border border-slate-700/50">
                <AlertTriangle className="w-4 h-4 text-warning" /> No Socials Provided
              </div>
            )}
          </div>

          {/* Chart Section */}
          <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-sm font-medium text-slate-300 mb-6 flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" /> 
              Price History (24h)
            </h3>
            
            <div className="h-64 w-full">
              {snapshotsLoading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
                </div>
              ) : chartData.length > 1 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis 
                      dataKey="time" 
                      stroke="#64748b" 
                      fontSize={12} 
                      tickLine={false}
                      axisLine={false}
                      minTickGap={30}
                    />
                    <YAxis 
                      domain={['auto', 'auto']}
                      stroke="#64748b" 
                      fontSize={12}
                      tickFormatter={(val) => `$${val.toFixed(6)}`}
                      tickLine={false}
                      axisLine={false}
                      width={80}
                    />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }}
                      itemStyle={{ color: '#10b981' }}
                      labelStyle={{ color: '#94a3b8', marginBottom: '0.25rem' }}
                      formatter={(value: any) => [`$${Number(value).toFixed(8)}`, 'Price']}
                      labelFormatter={(_: any, payload: any) => payload[0]?.payload?.fullDate || ''}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorPrice)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-2">
                  <AlertTriangle className="w-8 h-8 text-slate-600" />
                  <p>Not enough history collected yet.</p>
                  <p className="text-xs">The scanner takes snapshots every 5 minutes.</p>
                </div>
              )}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  )
}
