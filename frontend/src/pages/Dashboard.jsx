import React from 'react';
import { TrendingUp, Activity, ArrowRight, ShieldAlert, Sparkles, Filter } from 'lucide-react';
import Leaderboard from '../components/Leaderboard';
import HealthBadge from '../components/HealthBadge';

export default function Dashboard({
  sectors = [],
  onSelectSector,
  onOpenBacktest,
  selectedSector,
  asOfDate,
}) {
  // Breadth metrics
  const strongBuys = sectors.filter((s) => s.health_label === 'Strong Buy').length;
  const buys = sectors.filter((s) => s.health_label === 'Buy').length;
  const neutrals = sectors.filter((s) => s.health_label === 'Neutral').length;
  const avoids = sectors.filter((s) => s.health_label === 'Avoid' || s.health_label === 'Strong Avoid').length;

  const topPick = sectors.length > 0 ? sectors[0] : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top summary chips */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Top Pick */}
        <div className="bg-surface border border-subtle rounded p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-muted mb-2">
            <span className="font-body">Top Ranked Sector</span>
            <Sparkles className="w-3.5 h-3.5 text-brand" />
          </div>
          {topPick ? (
            <div>
              <div className="flex items-center justify-between">
                <span className="font-display text-xl font-bold text-primary">{topPick.sector}</span>
                <HealthBadge label={topPick.health_label} size="sm" />
              </div>
              <div className="text-xs font-mono text-muted mt-1">
                20D: <span className="text-signal-buy font-semibold">+{topPick.return_20d_pct?.toFixed(2)}%</span> · 5D Fwd: <span className="text-signal-buy font-semibold">+{topPick.predicted_return_5d_pct?.toFixed(2)}%</span>
              </div>
            </div>
          ) : (
            <div className="text-xs font-mono text-muted">Loading...</div>
          )}
        </div>

        {/* Bullish Breadth */}
        <div className="bg-surface border border-subtle rounded p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-muted mb-2">
            <span className="font-body">Bullish Sectors</span>
            <span className="w-2 h-2 rounded-full bg-signal-buy" />
          </div>
          <div>
            <div className="font-mono text-2xl font-bold text-signal-buy">
              {strongBuys + buys} <span className="text-xs font-normal text-muted">/ 8 Sectors</span>
            </div>
            <div className="text-xs font-mono text-muted mt-1">
              {strongBuys} Strong Buy · {buys} Buy
            </div>
          </div>
        </div>

        {/* Neutral / Cautious */}
        <div className="bg-surface border border-subtle rounded p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-muted mb-2">
            <span className="font-body">Neutral / Avoid Sectors</span>
            <span className="w-2 h-2 rounded-full bg-signal-avoid" />
          </div>
          <div>
            <div className="font-mono text-2xl font-bold text-signal-avoid">
              {avoids} <span className="text-xs font-normal text-muted">Avoid · {neutrals} Neutral</span>
            </div>
            <div className="text-xs font-mono text-muted mt-1">
              Dampened momentum vs NIFTY 50
            </div>
          </div>
        </div>

        {/* Backtest Action Card */}
        <div
          onClick={onOpenBacktest}
          className="bg-surface border border-brand/40 rounded p-4 flex flex-col justify-between hover:bg-surface-hover cursor-pointer transition-colors group"
        >
          <div className="flex items-center justify-between text-xs text-brand mb-2">
            <span className="font-semibold font-body">Rotation Strategy Backtest</span>
            <Activity className="w-4 h-4 text-brand" />
          </div>
          <div>
            <div className="font-mono text-sm font-semibold text-primary group-hover:text-brand flex items-center justify-between">
              <span>Strategy vs NIFTY 50</span>
              <ArrowRight className="w-4 h-4 text-brand transition-transform group-hover:translate-x-1" />
            </div>
            <div className="text-xs font-mono text-muted mt-1">
              CAGR: <span className="text-signal-buy font-semibold">+22.58%</span> vs +11.29% NIFTY
            </div>
          </div>
        </div>
      </div>

      {/* Main Container: Left Rail + Main Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Rail: Quick Navigation */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-surface border border-subtle rounded p-4">
            <h3 className="text-xs font-mono uppercase tracking-wider text-muted font-semibold pb-3 mb-3 border-b border-subtle">
              Sectors Directory
            </h3>
            <div className="space-y-1.5">
              {sectors.map((s) => {
                const isSelected = selectedSector === s.sector;
                return (
                  <button
                    key={s.sector}
                    onClick={() => onSelectSector(s.sector)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded text-xs font-mono transition-colors text-left cursor-pointer ${
                      isSelected
                        ? 'bg-brand-subtle text-brand border border-brand/30 font-semibold'
                        : 'text-primary hover:bg-surface-hover border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        s.health_label === 'Strong Buy' || s.health_label === 'Buy'
                          ? 'bg-signal-buy'
                          : s.health_label === 'Neutral'
                          ? 'bg-signal-neutral'
                          : 'bg-signal-avoid'
                      }`} />
                      <span>{s.sector}</span>
                    </div>
                    <span className="text-muted text-[11px]">
                      {s.return_20d_pct >= 0 ? '+' : ''}{s.return_20d_pct?.toFixed(1)}%
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Main Panel: Leaderboard Table */}
        <div className="lg:col-span-9 space-y-4">
          <Leaderboard
            sectors={sectors}
            onSelectSector={onSelectSector}
            selectedSector={selectedSector}
          />
        </div>
      </div>
    </div>
  );
}
