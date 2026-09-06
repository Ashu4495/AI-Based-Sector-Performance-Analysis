import React from 'react';
import { ArrowUpRight, ArrowDownRight, TrendingUp, ChevronRight } from 'lucide-react';
import HealthBadge from './HealthBadge';

export default function Leaderboard({ sectors = [], onSelectSector, selectedSector }) {
  if (!sectors || sectors.length === 0) {
    return (
      <div className="p-8 text-center bg-surface border border-subtle rounded text-muted font-mono text-sm">
        No sector leaderboard data available.
      </div>
    );
  }

  return (
    <div className="w-full bg-surface border border-subtle rounded overflow-hidden">
      <div className="px-5 py-4 border-b border-subtle flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div>
          <h2 className="font-display text-lg font-bold text-primary">NSE Sector Health Leaderboard</h2>
          <p className="text-xs text-muted font-body mt-0.5">
            Ranked by AI health classification and 20-day momentum against NIFTY 50 benchmark
          </p>
        </div>
        <div className="text-[11px] font-mono text-muted bg-base px-2.5 py-1 rounded border border-subtle">
          Sorted: Strong Buy → Strong Avoid
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-subtle bg-base/50 text-[11px] font-mono text-muted uppercase tracking-wider">
              <th className="py-3 px-4 font-medium">Rank & Sector</th>
              <th className="py-3 px-4 font-medium">AI Health Label</th>
              <th className="py-3 px-4 font-medium text-right">Latest Close (₹)</th>
              <th className="py-3 px-4 font-medium text-right">1D Δ</th>
              <th className="py-3 px-4 font-medium text-right">20D Return</th>
              <th className="py-3 px-4 font-medium text-right">20D vs NIFTY 50</th>
              <th className="py-3 px-4 font-medium text-right">RSI (14)</th>
              <th className="py-3 px-4 font-medium text-right">5D AI Forecast</th>
              <th className="py-3 px-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-subtle text-xs font-mono">
            {sectors.map((item, index) => {
              const isSelected = selectedSector === item.sector;
              const ret1d = item.return_1d_pct || 0;
              const ret20d = item.return_20d_pct || 0;
              const rel20d = item.rel_return_20d_pct || 0;
              const fwd5d = item.predicted_return_5d_pct || 0;

              return (
                <tr
                  key={item.sector}
                  onClick={() => onSelectSector(item.sector)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-brand-subtle/40 border-l-2 border-brand'
                      : 'hover:bg-surface-hover'
                  }`}
                >
                  {/* Rank & Sector */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-3">
                      <span className="text-muted text-[11px] w-4 font-mono font-medium">#{index + 1}</span>
                      <div>
                        <div className="font-semibold text-primary font-body text-sm flex items-center gap-1.5">
                          <span>{item.sector}</span>
                          <span className="text-xs font-normal text-muted font-body">({item.sector_name})</span>
                        </div>
                        <div className="text-[11px] text-muted font-body">{item.display_name}</div>
                      </div>
                    </div>
                  </td>

                  {/* Health Badge */}
                  <td className="py-3.5 px-4">
                    <HealthBadge label={item.health_label} size="sm" />
                  </td>

                  {/* Latest Close */}
                  <td className="py-3.5 px-4 text-right font-medium text-primary">
                    ₹{Number(item.latest_close || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>

                  {/* 1D Return */}
                  <td className={`py-3.5 px-4 text-right font-medium ${ret1d >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                    {ret1d >= 0 ? '+' : ''}{ret1d.toFixed(2)}%
                  </td>

                  {/* 20D Return */}
                  <td className={`py-3.5 px-4 text-right font-medium ${ret20d >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                    {ret20d >= 0 ? '+' : ''}{ret20d.toFixed(2)}%
                  </td>

                  {/* Relative 20D vs NIFTY 50 */}
                  <td className={`py-3.5 px-4 text-right font-medium ${rel20d >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                    {rel20d >= 0 ? '+' : ''}{rel20d.toFixed(2)}%
                  </td>

                  {/* RSI 14 */}
                  <td className="py-3.5 px-4 text-right text-muted">
                    <span className={item.rsi_14 > 70 ? 'text-signal-avoid font-semibold' : item.rsi_14 < 30 ? 'text-signal-buy font-semibold' : 'text-primary'}>
                      {item.rsi_14?.toFixed(1) || '50.0'}
                    </span>
                  </td>

                  {/* 5D Forecast */}
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex flex-col items-end">
                      <span className={`font-semibold ${fwd5d >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                        {fwd5d >= 0 ? '+' : ''}{fwd5d.toFixed(2)}%
                      </span>
                      <span className="text-[10px] text-muted font-body">({item.direction})</span>
                    </div>
                  </td>

                  {/* View action */}
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectSector(item.sector);
                      }}
                      className="p-1.5 rounded hover:bg-surface border border-subtle text-brand transition-colors inline-flex items-center justify-center cursor-pointer"
                      title={`Analyze ${item.sector}`}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
