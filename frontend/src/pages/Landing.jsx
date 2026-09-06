import React from 'react';
import { ArrowRight, BarChart2, Shield, BrainCircuit, LineChart, CheckCircle2 } from 'lucide-react';
import TickerStrip from '../components/TickerStrip';
import HealthBadge from '../components/HealthBadge';

export default function Landing({ sectors = [], onExplore, onSelectSector }) {
  const features = [
    {
      title: 'Categorical Health Labels',
      desc: 'Clear, institutional-style ratings (Strong Buy to Strong Avoid) without opaque numeric scores.',
      icon: Shield,
    },
    {
      title: 'Ridge Return Forecasts',
      desc: 'Interpretable 5-day return projections with 68% confidence intervals derived from price action.',
      icon: LineChart,
    },
    {
      title: 'SHAP Explainability',
      desc: 'TreeSHAP decomposes every prediction into top driving technical & relative-strength indicators.',
      icon: BrainCircuit,
    },
    {
      title: 'Monthly Rotation Backtest',
      desc: 'Transparently simulated rotation strategy benchmarked against NIFTY 50 from 2019 to 2026.',
      icon: BarChart2,
    },
  ];

  return (
    <div className="w-full space-y-10 pb-16">
      {/* 1. Live Ticker Strip */}
      <TickerStrip sectors={sectors} />

      {/* 2. Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-brand-subtle border border-brand/30 text-brand font-mono text-xs">
            <span>Portfolio Intelligence · NSE Sector Indices</span>
          </div>

          <h1 className="font-display text-4xl sm:text-5xl font-bold tracking-tight text-primary leading-[1.15]">
            Which NSE sectors deserve your attention this week.
          </h1>

          <p className="text-base sm:text-lg text-muted font-body leading-relaxed max-w-2xl">
            An explainable read on sector health, momentum, and near-term direction — built purely on historical OHLCV data, rigorous feature engineering, and interpretable ML.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <button
              onClick={onExplore}
              className="px-5 py-2.5 rounded bg-brand-subtle hover:bg-brand-subtle/80 text-brand border border-brand/40 font-mono text-sm font-semibold flex items-center gap-2 transition-all cursor-pointer shadow-sm"
              id="view-leaderboard-btn"
            >
              <span>View Sector Leaderboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <div className="text-xs font-mono text-muted">
              8 Sectors + NIFTY 50 Benchmark
            </div>
          </div>
        </div>
      </section>

      {/* 3. Live Sector Quick Snapshot Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border border-subtle rounded bg-surface p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-4 border-b border-subtle">
            <div>
              <h2 className="font-display text-lg font-bold text-primary">Current Sector Health Snapshot</h2>
              <p className="text-xs text-muted font-body">Click any sector to inspect its detailed indicators and SHAP attribution</p>
            </div>
            <button
              onClick={onExplore}
              className="text-xs font-mono text-brand hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>Full Leaderboard Table</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {sectors.map((sec) => (
              <div
                key={sec.sector}
                onClick={() => onSelectSector(sec.sector)}
                className="bg-base border border-subtle rounded p-3.5 hover:border-brand/50 hover:bg-surface-hover transition-all cursor-pointer flex flex-col justify-between"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="font-body font-bold text-primary text-sm">{sec.sector}</span>
                    <div className="text-[11px] text-muted truncate">{sec.display_name}</div>
                  </div>
                  <HealthBadge label={sec.health_label} size="sm" />
                </div>

                <div className="flex items-end justify-between pt-2 border-t border-subtle text-xs font-mono">
                  <div>
                    <div className="text-[10px] text-muted">Close</div>
                    <div className="font-medium text-primary">₹{Number(sec.latest_close || 0).toLocaleString('en-IN', { maximumFractionDigits: 1 })}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-muted">5D Forecast</div>
                    <div className={`font-semibold ${sec.predicted_return_5d_pct >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                      {sec.predicted_return_5d_pct >= 0 ? '+' : ''}{sec.predicted_return_5d_pct?.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. Feature Explainer Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border border-subtle rounded bg-surface p-6">
          <div className="max-w-2xl mb-6">
            <h2 className="font-display text-xl font-bold text-primary">How MarketPulse AI Evaluates a Sector</h2>
            <p className="text-xs text-muted font-body mt-1">
              Ground truth technical indicators and relative strength metrics derived strictly from yfinance OHLCV data.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div key={idx} className="bg-base border border-subtle rounded p-4 flex flex-col justify-between">
                  <div>
                    <div className="w-8 h-8 rounded bg-brand-subtle text-brand flex items-center justify-center mb-3">
                      <Icon className="w-4 h-4" />
                    </div>
                    <h3 className="font-body font-semibold text-sm text-primary mb-1">{feat.title}</h3>
                    <p className="text-xs text-muted font-body leading-relaxed">{feat.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Transparent Guarantees */}
          <div className="mt-6 pt-4 border-t border-subtle grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono text-muted">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-brand shrink-0" />
              <span>Zero black-box numeric scores</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-brand shrink-0" />
              <span>Strictly zero lookahead bias</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-brand shrink-0" />
              <span>Benchmarked vs NIFTY 50</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
