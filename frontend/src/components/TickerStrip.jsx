import React from 'react';

export default function TickerStrip({ sectors = [] }) {
  // If no sectors passed, use standard representation
  const items = sectors.length > 0 ? sectors : [
    { sector: 'IT', return_1d_pct: 1.20, latest_close: 30695.15 },
    { sector: 'BANK', return_1d_pct: -0.45, latest_close: 57369.65 },
    { sector: 'AUTO', return_1d_pct: 0.85, latest_close: 27099.75 },
    { sector: 'PHARMA', return_1d_pct: 0.32, latest_close: 26478.10 },
    { sector: 'FMCG', return_1d_pct: -0.15, latest_close: 48748.70 },
    { sector: 'METAL', return_1d_pct: 1.65, latest_close: 12436.95 },
    { sector: 'ENERGY', return_1d_pct: 0.22, latest_close: 39277.00 },
    { sector: 'REALTY', return_1d_pct: 1.40, latest_close: 918.70 },
  ];

  // Duplicate list to create seamless infinite marquee scroll
  const marqueeItems = [...items, ...items, ...items];

  return (
    <div className="w-full bg-surface border-y border-subtle overflow-hidden py-2 select-none">
      <div className="animate-ticker flex items-center gap-8 text-xs font-mono">
        {marqueeItems.map((item, idx) => {
          const isPos = (item.return_1d_pct || 0) >= 0;
          return (
            <div key={idx} className="flex items-center gap-2 shrink-0">
              <span className="font-semibold text-primary">{item.sector}</span>
              <span className="text-muted">₹{Number(item.latest_close || 0).toLocaleString('en-IN', { maximumFractionDigits: 1 })}</span>
              <span className={isPos ? 'text-signal-buy font-medium' : 'text-signal-avoid font-medium'}>
                {isPos ? '▲' : '▼'} {Math.abs(item.return_1d_pct || 0).toFixed(2)}%
              </span>
              <span className="text-muted opacity-30">|</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
