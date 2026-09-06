import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { Activity, TrendingUp, ShieldAlert, Award, Calendar, RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import HealthBadge from '../components/HealthBadge';

export default function Backtest() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    api
      .getBacktest()
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load backtest results');
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-6 h-6 text-brand animate-spin" />
        <span className="text-xs font-mono text-muted">Replaying monthly sector rotation backtest simulations...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-surface border border-signal-avoid/40 rounded p-6 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-signal-avoid mx-auto" />
          <h2 className="font-display text-lg font-bold text-primary">Could not load backtest simulation</h2>
          <p className="text-xs font-mono text-muted">{error}</p>
        </div>
      </div>
    );
  }

  const { metrics, equity_curve, trades_log, start_date, end_date, total_trading_days } = data;
  const strat = metrics.strategy;
  const bm = metrics.benchmark;
  const comp = metrics.comparison;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const pt = payload[0].payload;
      return (
        <div className="bg-surface border border-subtle p-3 rounded text-xs font-mono shadow-lg space-y-1">
          <div className="text-muted font-semibold pb-1 mb-1 border-b border-subtle flex items-center justify-between gap-4">
            <span>{pt.date}</span>
            {pt.holding && <span className="text-brand font-bold">Holding: {pt.holding}</span>}
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-[#3FA796] font-medium">AI Strategy:</span>
            <span className="text-primary font-bold">
              {pt.strategy_return_pct >= 0 ? '+' : ''}{pt.strategy_return_pct?.toFixed(2)}%
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-muted font-medium">NIFTY 50 Benchmark:</span>
            <span className="text-primary font-bold">
              {pt.benchmark_return_pct >= 0 ? '+' : ''}{pt.benchmark_return_pct?.toFixed(2)}%
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* 1. Header */}
      <div className="bg-surface border border-subtle rounded p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-brand" />
              <h1 className="font-display text-2xl font-bold text-primary">
                Monthly Sector Rotation Strategy Backtest
              </h1>
            </div>
            <p className="text-xs text-muted font-body mt-1 max-w-3xl leading-relaxed">
              Historical simulation: every 21 trading days (~1 month), rotate 100% portfolio capital into the sector with the highest AI health classification and relative momentum. Benchmarked strictly against NIFTY 50 buy-and-hold.
            </p>
          </div>

          <div className="text-xs font-mono text-muted bg-base p-3 rounded border border-subtle shrink-0">
            <div>Span: <strong className="text-primary">{start_date}</strong> to <strong className="text-primary">{end_date}</strong></div>
            <div>Sessions: <strong className="text-primary">{total_trading_days}</strong> ({comp.total_rebalances} Rebalances)</div>
          </div>
        </div>
      </div>

      {/* 2. Key Comparison Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Cumulative Return */}
        <div className="bg-surface border border-subtle rounded p-4">
          <div className="text-xs text-muted font-body mb-1">Cumulative Total Return</div>
          <div className="font-mono text-2xl font-bold text-signal-buy">
            +{strat.cumulative_return_pct?.toFixed(2)}%
          </div>
          <div className="text-xs font-mono text-muted mt-2 pt-2 border-t border-subtle flex justify-between">
            <span>NIFTY 50:</span>
            <span className="font-medium text-primary">+{bm.cumulative_return_pct?.toFixed(2)}%</span>
          </div>
        </div>

        {/* Annualized CAGR */}
        <div className="bg-surface border border-subtle rounded p-4">
          <div className="text-xs text-muted font-body mb-1">Annualized CAGR</div>
          <div className="font-mono text-2xl font-bold text-signal-buy">
            +{strat.cagr_pct?.toFixed(2)}%
          </div>
          <div className="text-xs font-mono text-muted mt-2 pt-2 border-t border-subtle flex justify-between">
            <span>Alpha (Excess CAGR):</span>
            <span className="font-bold text-signal-buy">+{comp.excess_cagr_pct?.toFixed(2)}%</span>
          </div>
        </div>

        {/* Sharpe Ratio */}
        <div className="bg-surface border border-subtle rounded p-4">
          <div className="text-xs text-muted font-body mb-1">Sharpe Ratio (Rf = 6.5%)</div>
          <div className="font-mono text-2xl font-bold text-primary">
            {strat.sharpe_ratio?.toFixed(2)}
          </div>
          <div className="text-xs font-mono text-muted mt-2 pt-2 border-t border-subtle flex justify-between">
            <span>NIFTY 50 Sharpe:</span>
            <span className="font-medium text-primary">{bm.sharpe_ratio?.toFixed(2)}</span>
          </div>
        </div>

        {/* Max Drawdown & Win Rate */}
        <div className="bg-surface border border-subtle rounded p-4">
          <div className="text-xs text-muted font-body mb-1">Monthly Win Rate vs Benchmark</div>
          <div className="font-mono text-2xl font-bold text-brand">
            {comp.monthly_win_rate_pct?.toFixed(1)}%
          </div>
          <div className="text-xs font-mono text-muted mt-2 pt-2 border-t border-subtle flex justify-between">
            <span>Max Drawdown:</span>
            <span className="font-medium text-signal-avoid">{strat.max_drawdown_pct?.toFixed(2)}%</span>
          </div>
        </div>
      </div>

      {/* 3. Equity Curve Chart */}
      <div className="bg-surface border border-subtle rounded p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-display text-base font-bold text-primary">Cumulative Equity Growth (% Return)</h3>
            <p className="text-xs text-muted font-body">
              Normalized performance comparison of ₹100,000 invested in October 2019
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-[#3FA796]" />
              <span className="text-[#3FA796] font-semibold">AI Sector Rotation</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-[#8FA0B8]" />
              <span className="text-muted">NIFTY 50 Buy & Hold</span>
            </div>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={equity_curve} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="3 3" opacity={0.5} />
              <XAxis
                dataKey="date"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
                tickLine={{ stroke: 'var(--border-subtle)' }}
                minTickGap={50}
              />
              <YAxis
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
                tickLine={{ stroke: 'var(--border-subtle)' }}
                orientation="right"
                tickFormatter={(v) => `${v > 0 ? '+' : ''}${v}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* Benchmark Line */}
              <Line
                type="monotone"
                dataKey="benchmark_return_pct"
                name="NIFTY 50 Benchmark"
                stroke="var(--text-muted)"
                strokeWidth={1.6}
                dot={false}
                isAnimationActive={false}
              />

              {/* Strategy Line */}
              <Line
                type="monotone"
                dataKey="strategy_return_pct"
                name="AI Sector Rotation"
                stroke="#3FA796"
                strokeWidth={2.4}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Recent Monthly Rebalance Trade History */}
      <div className="bg-surface border border-subtle rounded overflow-hidden">
        <div className="px-5 py-4 border-b border-subtle flex items-center justify-between">
          <h3 className="font-display text-base font-bold text-primary">
            Recent Monthly Sector Rebalancing Decisions
          </h3>
          <span className="text-xs font-mono text-muted">Last 12 Monthly Sessions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-subtle bg-base/50 text-[11px] font-mono text-muted uppercase tracking-wider">
                <th className="py-2.5 px-4">Rebalance Date</th>
                <th className="py-2.5 px-4">Selected Sector</th>
                <th className="py-2.5 px-4">Health Label at Entry</th>
                <th className="py-2.5 px-4 text-right">Entry Index Level</th>
                <th className="py-2.5 px-4 text-right">Strategy Capital (₹)</th>
                <th className="py-2.5 px-4 text-right">Benchmark Capital (₹)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-subtle text-xs font-mono">
              {trades_log.map((trade, idx) => (
                <tr key={idx} className="hover:bg-surface-hover transition-colors">
                  <td className="py-3 px-4 font-medium text-primary">{trade.rebalance_date}</td>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-brand font-body">{trade.selected_sector}</span>{' '}
                    <span className="text-muted font-body text-[11px]">({trade.selected_name})</span>
                  </td>
                  <td className="py-3 px-4">
                    <HealthBadge label={trade.health_label} size="sm" />
                  </td>
                  <td className="py-3 px-4 text-right text-primary">₹{trade.entry_price.toLocaleString('en-IN')}</td>
                  <td className="py-3 px-4 text-right text-signal-buy font-semibold">
                    ₹{Number(trade.strategy_equity).toLocaleString('en-IN')}
                  </td>
                  <td className="py-3 px-4 text-right text-muted">
                    ₹{Number(trade.benchmark_equity).toLocaleString('en-IN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
