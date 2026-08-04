import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Terminal, Download } from 'lucide-react'

const API_BASE = '/api'

export default function Logs() {
  const [logType, setLogType] = useState('worker')
  const bottomRef = useRef<HTMLDivElement>(null)

  const { data } = useQuery({
    queryKey: ['logs', logType],
    queryFn: async () => (await axios.get(`${API_BASE}/logs/${logType}?lines=200`)).data,
    refetchInterval: 10000 // Refresh every 10 seconds
  })

  const logs = data?.logs || []

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const handleDownload = () => {
    const blob = new Blob([logs.join('')], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${logType}.log`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Terminal className="w-6 h-6 text-primary" />
          System Logs
        </h1>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handleDownload}
            className="flex items-center gap-2 bg-primary/10 hover:bg-primary/20 text-primary px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-primary/20"
          >
            <Download className="w-4 h-4" />
            Download {logType}.log
          </button>
        </div>
      </div>

      <div className="flex gap-2">
        {['worker', 'trades', 'errors'].map(type => (
          <button
            key={type}
            onClick={() => setLogType(type)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
              logType === type 
                ? 'bg-primary text-white' 
                : 'bg-surface border border-slate-700/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      <div className="flex-1 bg-black border border-slate-700/50 rounded-xl overflow-hidden relative">
        <div className="absolute top-0 inset-x-0 h-4 bg-gradient-to-b from-black to-transparent z-10 pointer-events-none" />
        
        <div className="h-full overflow-y-auto p-4 font-mono text-xs md:text-sm">
          {logs.length === 0 ? (
            <div className="text-slate-600">No logs found for {logType}.log</div>
          ) : (
            logs.map((line: string, i: number) => {
              // Basic coloring for log levels
              let colorClass = 'text-slate-300'
              if (line.includes('ERROR')) colorClass = 'text-danger'
              else if (line.includes('WARNING')) colorClass = 'text-warning'
              else if (line.includes('INFO')) colorClass = 'text-primary'
              else if (line.includes('BUY_SIGNAL')) colorClass = 'text-success font-bold'

              return (
                <div key={i} className={`whitespace-pre-wrap break-words leading-relaxed ${colorClass}`}>
                  {line}
                </div>
              )
            })
          )}
          <div ref={bottomRef} />
        </div>
        
        <div className="absolute bottom-0 inset-x-0 h-4 bg-gradient-to-t from-black to-transparent z-10 pointer-events-none" />
      </div>
    </div>
  )
}
