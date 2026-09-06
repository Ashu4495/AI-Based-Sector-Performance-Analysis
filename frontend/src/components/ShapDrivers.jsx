import React from 'react';
import { Sparkles, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function ShapDrivers({ drivers = [], healthLabel = 'Health Signal' }) {
  if (!drivers || drivers.length === 0) {
    return (
      <div className="p-4 bg-surface border border-subtle rounded text-muted font-mono text-xs text-center">
        No feature explainability signals available.
      </div>
    );
  }

  return (
    <div className="w-full bg-surface border border-subtle rounded p-4">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-subtle">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand" />
          <h3 className="font-display text-base font-bold text-primary">Key AI Drivers & Explainability (SHAP)</h3>
        </div>
        <span className="text-[11px] font-mono text-muted bg-base px-2 py-0.5 rounded border border-subtle">
          TreeSHAP Attribution
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {drivers.map((driver, index) => {
          const isPositive = driver.direction === 'positive';
          const maxShap = 0.15;
          const barWidth = Math.min(100, Math.max(15, (driver.impact_magnitude / maxShap) * 100));

          return (
            <div
              key={index}
              className="bg-base border border-subtle rounded p-3 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <span className="text-xs font-semibold text-primary font-body">
                    {driver.display_name}
                  </span>
                  <span
                    className={`inline-flex items-center gap-0.5 text-[10px] font-mono font-medium px-1.5 py-0.2 rounded border ${
                      isPositive
                        ? 'text-signal-buy bg-signal-buy border-signal-buy'
                        : 'text-signal-avoid bg-signal-avoid border-signal-avoid'
                    }`}
                  >
                    {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    <span>{isPositive ? 'Reinforcing' : 'Dampening'}</span>
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs font-mono text-muted mb-2">
                  <span>Observed: <strong className="text-primary">{driver.formatted_value}</strong></span>
                  <span>Attribution: <strong>{driver.shap_value > 0 ? '+' : ''}{driver.shap_value?.toFixed(4)}</strong></span>
                </div>

                {/* Impact strength bar */}
                <div className="w-full bg-surface h-1.5 rounded-full overflow-hidden mb-2">
                  <div
                    className={`h-full rounded-full ${isPositive ? 'bg-signal-buy' : 'bg-signal-avoid'}`}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>
              </div>

              <p className="text-[11px] text-muted font-body leading-relaxed">
                {driver.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
