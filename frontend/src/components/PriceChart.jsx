import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import HealthBadge from './HealthBadge';

export default function PriceChart({ priceHistory = [], sectorName = 'Sector' }) {
  const [showIndicators, setShowIndicators] = useState(true);

  if (!priceHistory || priceHistory.length === 0) {
    return (
      <div className="h-72 flex items-center justify-center bg-surface border border-subtle rounded text-muted font-mono text-xs">
        No price history available for chart rendering.
      </div>
    );
  }

  // Find min/max for tight Y-axis domain
  const closes = priceHistory.map((p) => p.close).filter(Boolean);
  const minClose = Math.min(...closes);
  const maxClose = Math.max(...closes);
  const padding = (maxClose - minClose) * 0.05;

  const yDomain = [Math.floor(minClose - padding), Math.ceil(maxClose + padding)];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-surface border border-subtle p-3 rounded text-xs font-mono shadow-lg">
          <div className="text-muted font-semibold pb-1.5 mb-1.5 border-b border-subtle flex items-center justify-between gap-4">
            <span>{data.date}</span>
            {data.health_label && <HealthBadge label={data.health_label} size="sm" />}
          </div>
          <div className="space-y-1">
            <div className="flex justify-between gap-4">
              <span className="text-muted">Close:</span>
              <span className="font-semibold text-primary">₹{data.close?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
            {data.ema_20 && (
              <div className="flex justify-between gap-4">
                <span className="text-[#3FA796]">EMA 20:</span>
                <span className="text-primary">₹{data.ema_20?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            )}
            {data.sma_50 && (
              <div className="flex justify-between gap-4">
                <span className="text-[#C99A3E]">SMA 50:</span>
                <span className="text-primary">₹{data.sma_50?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </div>
            )}
            {data.rsi_14 && (
              <div className="flex justify-between gap-4 pt-1 border-t border-subtle">
                <span className="text-muted">RSI (14):</span>
                <span className={data.rsi_14 > 70 ? 'text-signal-avoid font-semibold' : data.rsi_14 < 30 ? 'text-signal-buy font-semibold' : 'text-primary'}>
                  {data.rsi_14}
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full bg-surface border border-subtle rounded p-4">
      {/* Chart Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="font-display text-base font-bold text-primary">Price Action & Trend Moving Averages</h3>
          <p className="text-xs text-muted font-body">
            Daily historical close with 20-Day EMA and 50-Day SMA trend signals
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <button
            onClick={() => setShowIndicators(!showIndicators)}
            className={`px-2.5 py-1 rounded border transition-colors cursor-pointer ${
              showIndicators
                ? 'bg-brand-subtle text-brand border-brand/40'
                : 'bg-base text-muted border-subtle'
            }`}
          >
            {showIndicators ? 'Hide Overlays' : 'Show EMA/SMA'}
          </button>
        </div>
      </div>

      {/* Main Price Chart */}
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={priceHistory} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="3 3" opacity={0.5} />
            <XAxis
              dataKey="date"
              stroke="var(--text-muted)"
              tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
              tickLine={{ stroke: 'var(--border-subtle)' }}
              minTickGap={40}
            />
            <YAxis
              domain={yDomain}
              stroke="var(--text-muted)"
              tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
              tickLine={{ stroke: 'var(--border-subtle)' }}
              tickFormatter={(val) => `₹${Number(val).toLocaleString('en-IN')}`}
              orientation="right"
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* Price Line */}
            <Line
              type="monotone"
              dataKey="close"
              name="Close Price"
              stroke="var(--text-primary)"
              strokeWidth={1.8}
              dot={false}
              isAnimationActive={false}
            />

            {/* EMA 20 */}
            {showIndicators && (
              <Line
                type="monotone"
                dataKey="ema_20"
                name="20-Day EMA"
                stroke="#3FA796"
                strokeWidth={1.4}
                strokeDasharray="4 2"
                dot={false}
                isAnimationActive={false}
              />
            )}

            {/* SMA 50 */}
            {showIndicators && (
              <Line
                type="monotone"
                dataKey="sma_50"
                name="50-Day SMA"
                stroke="#C99A3E"
                strokeWidth={1.4}
                dot={false}
                isAnimationActive={false}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Sub-chart: Volume & Momentum */}
      <div className="h-20 w-full mt-2 pt-2 border-t border-subtle">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={priceHistory} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
            <XAxis dataKey="date" hide />
            <YAxis
              stroke="var(--text-muted)"
              tick={{ fill: 'var(--text-muted)', fontSize: 9, fontFamily: 'var(--font-mono)' }}
              orientation="right"
              tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`}
            />
            <Bar dataKey="volume" fill="var(--text-muted)" opacity={0.3} maxBarSize={6} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
