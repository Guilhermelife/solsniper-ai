import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Save, CheckCircle2, Download, Upload, RotateCcw, Info } from 'lucide-react'

const API_BASE = '/api'

const DEFAULT_CONFIG = {
  // Position Sizing & Portfolio Manager
  position_size_mode: "FIXED_USD",
  default_position_size: 20.0,
  wallet_allocation_pct: 10.0,
  risk_per_trade_pct: 2.0,
  kelly_multiplier: 0.5,
  max_open_positions: 5,
  max_wallet_exposure_pct: 80.0,
  position_replacement_enabled: false,
  replacement_threshold_pct: -10.0,
  priority_difference_threshold: 20.0,
  max_positions_per_token: 1,
  
  // Entry Filters
  min_ai_score: 90.0,
  min_priority_score: 80.0,
  min_freshness_score: 30.0,
  min_liquidity: 1000.0,
  min_volume: 5000.0,
  min_market_cap: 5000.0,
  max_market_cap: 500000.0,
  min_buy_sell_ratio: 1.5,
  min_momentum: 10.0,
  max_token_age_minutes: 1440,
  allowed_dexes: "raydium,pumpfun,meteora,orca,pumpswap",
  
  // Exit Strategy
  trailing_stop_pct: 15.0,
  stop_loss_pct: -20.0,
  break_even_trigger_pct: 20.0,
  dynamic_trailing_stop: true,
  min_profit_before_trailing_pct: 10.0,
  trend_exit_sensitivity: 5.0,
  momentum_exit_threshold: -5.0,
  
  // Re-Entry
  reentry_enabled: true,
  reentry_cooldown_minutes: 60,
  max_reentries: 3,
  pullback_pct: -15.0,
  breakout_confirmation: true,
  
  // Scanner
  scan_interval_seconds: 30,
  max_tokens_per_scan: 60,
  watchlist_size: 100,
  signal_lifetime_hours: 6.0,
  max_cached_signals: 1000,
  signal_cooldown_hours: 6.0,
  
  // Paper Trading
  paper_initial_wallet: 50.0,
  paper_trading_fee_pct: 0.25,
  paper_slippage_pct: 1.0,
  paper_default_take_profit_pct: 1000.0,
  paper_default_stop_loss_pct: -50.0
}

export default function Configuration() {
  const queryClient = useQueryClient()
  const [localConfig, setLocalConfig] = useState<any>({})
  const [successMsg, setSuccessMsg] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: config, isLoading } = useQuery({
    queryKey: ['config'],
    queryFn: async () => (await axios.get(`${API_BASE}/config`)).data,
    refetchInterval: false
  })

  useEffect(() => {
    if (config) {
      setLocalConfig(config)
    }
  }, [config])

  const updateMutation = useMutation({
    mutationFn: async (updatedConfig: any) => {
      await axios.put(`${API_BASE}/config/`, updatedConfig)
    },
    onSuccess: () => {
      setSuccessMsg('Configuration updated dynamically. The engine is running with these settings now.')
      setTimeout(() => setSuccessMsg(''), 5000)
      queryClient.invalidateQueries({ queryKey: ['config'] })
    }
  })

  const handleChange = (key: string, value: any) => {
    setLocalConfig((prev: any) => ({ ...prev, [key]: value }))
  }

  const handleSaveAll = () => {
    const cleanedConfig = { ...localConfig }
    for (const key in cleanedConfig) {
      if (cleanedConfig[key] === '') {
        cleanedConfig[key] = null
      } else if (typeof cleanedConfig[key] === 'string' && !isNaN(Number(cleanedConfig[key])) && cleanedConfig[key].trim() !== '') {
        cleanedConfig[key] = Number(cleanedConfig[key])
      }
    }
    updateMutation.mutate(cleanedConfig)
  }

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(localConfig, null, 2))
    const downloadAnchorNode = document.createElement('a')
    downloadAnchorNode.setAttribute("href", dataStr)
    downloadAnchorNode.setAttribute("download", "solsniper_strategy.json")
    document.body.appendChild(downloadAnchorNode)
    downloadAnchorNode.click()
    downloadAnchorNode.remove()
  }

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const imported = JSON.parse(event.target?.result as string)
        setLocalConfig(imported)
        setSuccessMsg('Configuration imported successfully! Remember to Save.')
        setTimeout(() => setSuccessMsg(''), 5000)
      } catch (err) {
        alert("Failed to parse JSON")
      }
    }
    reader.readAsText(file)
  }

  const handleResetSection = (keys: string[]) => {
    const newConfig = { ...localConfig }
    keys.forEach(k => {
      if (DEFAULT_CONFIG.hasOwnProperty(k)) {
        newConfig[k] = (DEFAULT_CONFIG as any)[k]
      }
    })
    setLocalConfig(newConfig)
  }

  const handleResetAll = () => {
    if(confirm("Are you sure you want to reset all strategy parameters to their defaults?")) {
      setLocalConfig({ ...DEFAULT_CONFIG, id: localConfig.id, updated_at: localConfig.updated_at })
    }
  }

  if (isLoading) {
    return <div className="p-6 text-slate-400">Loading configuration...</div>
  }

  const renderField = (key: string, label: string, desc: string, type: 'text' | 'number' | 'boolean' | 'select' = 'number', options?: string[], step?: string) => {
    return (
      <div key={key} className="flex flex-col gap-1 bg-slate-800/30 p-4 rounded-lg border border-slate-700/50 hover:border-slate-600 transition-colors">
        <label className="text-sm font-semibold text-slate-200 flex items-center justify-between">
          {label}
          <div className="group relative cursor-help">
            <Info className="w-4 h-4 text-slate-400 hover:text-primary" />
            <div className="absolute right-0 w-48 p-2 bg-slate-900 border border-slate-700 text-xs text-slate-300 rounded shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              {desc}
            </div>
          </div>
        </label>
        
        {type === 'boolean' ? (
          <select
            value={localConfig[key] ? 'true' : 'false'}
            onChange={e => handleChange(key, e.target.value === 'true')}
            className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-white focus:outline-none focus:border-primary text-sm"
          >
            <option value="true">Enabled</option>
            <option value="false">Disabled</option>
          </select>
        ) : type === 'select' && options ? (
          <select
            value={localConfig[key] || ''}
            onChange={e => handleChange(key, e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-white focus:outline-none focus:border-primary text-sm"
          >
            {options.map(opt => <option key={opt} value={opt}>{opt.replace('_', ' ')}</option>)}
          </select>
        ) : (
          <input
            type={type}
            step={step || "any"}
            value={localConfig[key] ?? ''}
            onChange={e => handleChange(key, e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-white focus:outline-none focus:border-primary text-sm font-mono"
          />
        )}
      </div>
    )
  }

  const renderSection = (title: string, colorClass: string, fields: React.ReactNode, keys: string[]) => (
    <details className="group bg-surface border border-slate-700/50 rounded-xl overflow-hidden [&_summary::-webkit-details-marker]:hidden" open>
      <summary className={`flex items-center justify-between p-4 cursor-pointer hover:bg-slate-800/50 transition-colors`}>
        <h2 className={`text-lg font-semibold ${colorClass}`}>{title}</h2>
        <div className="flex items-center gap-4">
          <button onClick={(e) => { e.preventDefault(); handleResetSection(keys); }} className="text-xs text-slate-400 hover:text-white px-2 py-1 bg-slate-800 rounded">Reset</button>
          <span className="text-slate-400 group-open:rotate-180 transition-transform duration-200">
            ▼
          </span>
        </div>
      </summary>
      <div className="p-4 pt-0 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 border-t border-slate-700/50 mt-2 pt-4">
        {fields}
      </div>
    </details>
  )

  return (
    <div className="space-y-6 max-w-6xl pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Strategy Control Center</h1>
          <p className="text-sm text-slate-400 mt-1">Single source of truth for all bot behaviors.</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <input type="file" accept=".json" ref={fileInputRef} className="hidden" onChange={handleImport} />
          <button onClick={() => fileInputRef.current?.click()} className="btn-secondary flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-sm text-white">
            <Upload className="w-4 h-4" /> Import
          </button>
          <button onClick={handleExport} className="btn-secondary flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-sm text-white">
            <Download className="w-4 h-4" /> Export
          </button>
          <button onClick={handleResetAll} className="btn-secondary flex items-center gap-2 px-3 py-2 bg-red-900/30 hover:bg-red-900/50 border border-red-800 rounded text-sm text-red-200">
            <RotateCcw className="w-4 h-4" /> Reset All
          </button>
          <button 
            onClick={handleSaveAll}
            disabled={updateMutation.isPending}
            className="px-6 py-2 bg-primary hover:bg-primary/90 disabled:bg-slate-700 text-white rounded-md font-medium transition-colors flex items-center gap-2 shadow-lg shadow-primary/20"
          >
            <Save className="w-4 h-4" />
            Save & Apply Live
          </button>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 bg-success/10 border border-success/20 rounded-lg text-success text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="w-5 h-5" />
          {successMsg}
        </div>
      )}

      <div className="space-y-4">
        {renderSection('Scanner & Market Cap', 'text-cyan-400', <>
          {renderField('scan_interval_seconds', 'Scan Interval (s)', 'How often the bot polls for new tokens', 'number')}
          {renderField('max_tokens_per_scan', 'Max Tokens Per Scan', 'Limit tokens evaluated per cycle', 'number')}
          {renderField('watchlist_size', 'Watchlist Size', 'Max tokens tracked simultaneously', 'number')}
          {renderField('signal_cooldown_hours', 'Global Signal Cooldown (h)', 'Wait time before rescanning ignored tokens', 'number')}
          {renderField('signal_lifetime_hours', 'Signal Lifetime (h)', 'How long to keep signals in DB', 'number')}
          {renderField('max_cached_signals', 'Max Cached Signals', 'Max signals in memory', 'number')}
        </>, ['scan_interval_seconds', 'max_tokens_per_scan', 'watchlist_size', 'signal_cooldown_hours', 'signal_lifetime_hours', 'max_cached_signals'])}

        {renderSection('Entry Strategy (AI & Filters)', 'text-emerald-400', <>
          {renderField('min_ai_score', 'Min AI Score (0-100)', 'Base score needed to buy', 'number')}
          {renderField('min_priority_score', 'Min Priority Score', 'Combined AI + Freshness + Volume score', 'number')}
          {renderField('min_freshness_score', 'Min Freshness Score', 'Score based on age and previous price pumps', 'number')}
          {renderField('min_liquidity', 'Min Liquidity ($)', 'Minimum USD liquidity to enter', 'number')}
          {renderField('min_volume', 'Min 24h Volume ($)', 'Minimum 24h USD volume', 'number')}
          {renderField('min_market_cap', 'Min Market Cap ($)', 'Minimum fully diluted valuation', 'number')}
          {renderField('max_market_cap', 'Max Market Cap ($)', 'Maximum fully diluted valuation', 'number')}
          {renderField('min_buy_sell_ratio', 'Min Buy/Sell Ratio', 'Minimum ratio of buys vs sells', 'number', [], '0.1')}
          {renderField('min_momentum', 'Min Momentum (%)', 'Minimum short-term price momentum', 'number')}
          {renderField('max_token_age_minutes', 'Max Token Age (min)', 'Do not buy tokens older than this', 'number')}
          {renderField('allowed_dexes', 'Allowed DEXes', 'Comma separated list of allowed exchanges', 'text')}
        </>, ['min_ai_score', 'min_priority_score', 'min_freshness_score', 'min_liquidity', 'min_volume', 'min_market_cap', 'max_market_cap', 'min_buy_sell_ratio', 'min_momentum', 'max_token_age_minutes', 'allowed_dexes'])}

        {renderSection('Exit Strategy (Trend Following)', 'text-red-400', <>
          {renderField('trailing_stop_pct', 'Trailing Stop (%)', 'Distance from highest price to exit', 'number')}
          {renderField('stop_loss_pct', 'Hard Stop Loss (%)', 'Maximum loss from entry price (negative value)', 'number')}
          {renderField('dynamic_trailing_stop', 'Dynamic Trailing Stop', 'Adjust trailing stop based on momentum', 'boolean')}
          {renderField('break_even_trigger_pct', 'Break Even Trigger (%)', 'Profit required to move stop loss to entry price', 'number')}
          {renderField('min_profit_before_trailing_pct', 'Min Profit Before Trailing (%)', 'Wait for this profit before activating trailing stop', 'number')}
          {renderField('trend_exit_sensitivity', 'Trend Exit Sensitivity', 'How fast to react to trend reversals', 'number')}
          {renderField('momentum_exit_threshold', 'Momentum Exit Threshold', 'Exit if momentum drops below this value', 'number')}
        </>, ['trailing_stop_pct', 'stop_loss_pct', 'dynamic_trailing_stop', 'break_even_trigger_pct', 'min_profit_before_trailing_pct', 'trend_exit_sensitivity', 'momentum_exit_threshold'])}

        {renderSection('Position Sizing & Portfolio Management', 'text-amber-400', <>
          {renderField('position_size_mode', 'Position Size Mode', 'How to calculate trade sizes', 'select', ['FIXED_USD', 'PERCENTAGE', 'RISK_BASED', 'KELLY', 'AI_WEIGHTED'])}
          {renderField('default_position_size', 'Default Size ($ or %)', 'Amount based on mode', 'number')}
          {renderField('wallet_allocation_pct', 'Wallet Allocation (%)', 'Percent of wallet for PERCENTAGE mode', 'number')}
          {renderField('risk_per_trade_pct', 'Risk Per Trade (%)', 'Percent of wallet to risk per trade', 'number')}
          {renderField('kelly_multiplier', 'Kelly Multiplier', 'Fractional Kelly bet sizing', 'number', [], '0.1')}
          {renderField('max_open_positions', 'Max Open Positions', 'Max concurrent trades', 'number')}
          {renderField('max_wallet_exposure_pct', 'Max Wallet Exposure (%)', 'Max % of wallet deployed at once', 'number')}
          {renderField('position_replacement_enabled', 'Position Replacement', 'Replace worst performing trade if better signal arrives', 'boolean')}
          {renderField('replacement_threshold_pct', 'Replacement Threshold (%)', 'Replace trades doing worse than this', 'number')}
          {renderField('priority_difference_threshold', 'Priority Diff Threshold', 'New signal must be this much better to replace', 'number')}
          {renderField('max_positions_per_token', 'Max Positions / Token', 'Pyramiding limit per token', 'number')}
        </>, ['position_size_mode', 'default_position_size', 'wallet_allocation_pct', 'risk_per_trade_pct', 'kelly_multiplier', 'max_open_positions', 'max_wallet_exposure_pct', 'position_replacement_enabled', 'replacement_threshold_pct', 'priority_difference_threshold', 'max_positions_per_token'])}

        {renderSection('Re-Entry Engine', 'text-fuchsia-400', <>
          {renderField('reentry_enabled', 'Enable Re-Entries', 'Allow buying the same token again after exit', 'boolean')}
          {renderField('max_reentries', 'Max Re-entries', 'Maximum times to re-enter a token', 'number')}
          {renderField('reentry_cooldown_minutes', 'Re-Entry Cooldown (min)', 'Wait time before re-entry is allowed', 'number')}
          {renderField('pullback_pct', 'Pullback Required (%)', 'Price drop required before re-entry', 'number')}
          {renderField('breakout_confirmation', 'Breakout Confirmation', 'Require price to break out before re-entering', 'boolean')}
        </>, ['reentry_enabled', 'max_reentries', 'reentry_cooldown_minutes', 'pullback_pct', 'breakout_confirmation'])}

        {renderSection('Paper Trading Simulation', 'text-slate-400', <>
          {renderField('paper_initial_wallet', 'Initial Wallet Balance ($)', 'Starting capital for simulator (req reset)', 'number')}
          {renderField('paper_trading_fee_pct', 'Trading Fee (%)', 'Simulated exchange fee', 'number', [], '0.01')}
          {renderField('paper_slippage_pct', 'Slippage Penalty (%)', 'Simulated execution slippage', 'number', [], '0.1')}
          {renderField('paper_default_take_profit_pct', 'Default Take Profit (%)', 'Hard TP for simulator safety', 'number')}
          {renderField('paper_default_stop_loss_pct', 'Default Stop Loss (%)', 'Hard SL for simulator safety', 'number')}
        </>, ['paper_initial_wallet', 'paper_trading_fee_pct', 'paper_slippage_pct', 'paper_default_take_profit_pct', 'paper_default_stop_loss_pct'])}
      </div>

    </div>
  )
}
