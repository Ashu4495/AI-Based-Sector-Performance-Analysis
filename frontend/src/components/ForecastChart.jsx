import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, Target } from 'lucide-react';

export default function ForecastChart({ forecast, latestClose, recentHistory = [] }) {
  if (!forecast) return null;

  // Build 5-day future projected points
  const recentSlice = recentHistory.slice(-10);
  const basePrice = latestClose || (recentSlice.length > 0 ? recentSlice[recentSlice.length - 1].close : 10000);
  
  const fwdReturn = (forecast.predicted_return_pct || 0) / 100;
  const lowerReturn = (forecast.confidence_lower_pct || 0) / 100;
  const upperReturn = (forecast.confidence_upper_pct || 0) / 100;

  const targetPrice = basePrice * (1 + fwdReturn);
  const targetLower = basePrice * (1 + lowerReturn);
  const targetUpper = basePrice * (1 + upperReturn);

  // Construct continuous chart series: 10 past days + 5 forecast days
  const chartData = recentSlice.map((pt, idx) => ({
    label: pt.date.slice(5), // MM-DD
    actualClose: pt.close,
    forecastPrice: null,
    lowerBound: null,
    upperBound: null,
    isFuture: false,
  }));

  // Anchor point at latest date
  if (chartData.length > 0) {
    const lastIdx = chartData.length - 1;
    chartData[lastIdx].forecastPrice = basePrice;
    chartData[lastIdx].lowerBound = basePrice;
    chartData[lastIdx].upperBound = basePrice;
  }

  // Add 5 forward days
  for (let day = 1; day <= 5; day++) {
    const progress = day / 5;
    const interpolatedTarget = basePrice + (targetPrice - basePrice) * progress;
    const interpolatedLower = basePrice + (targetLower - basePrice) * progress;
    const interpolatedUpper = basePrice + (targetUpper - basePrice) * progress;

    chartData.push({
      label: `+${day}d`,
      actualClose: null,
      forecastPrice: Math.round(interpolatedTarget * 100) / 100,
      lowerBound: Math.round(interpolatedLower * 100) / 100,
      upperBound: Math.round(interpolatedUpper * 100) / 100,
      isFuture: true,
    });
  }

  const isBullish = forecast.direction === 'Bullish';
  const isBearish = forecast.direction === 'Bearish';

  return (
    <div className="w-full bg-surface border border-subtle rounded p-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-3 border-b border-subtle">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-brand" />
          <h3 className="font-display text-base font-bold text-primary">5-Day AI Return Forecast</h3>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-base border border-subtle font-mono text-xs">
            <span className="text-muted">Target:</span>
            <span className={`font-semibold ${forecast.predicted_return_pct >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
              {forecast.predicted_return_pct >= 0 ? '+' : ''}{forecast.predicted_return_pct?.toFixed(2)}%
            </span>
          </div>

          <div className={`flex items-center gap-1 px-2.5 py-1 rounded border font-mono text-xs font-semibold ${
            isBullish
              ? 'bg-signal-buy text-signal-buy border-signal-buy'
              : isBearish
              ? 'bg-signal-avoid text-signal-avoid border-signal-avoid'
              : 'bg-signal-neutral text-signal-neutral border-signal-neutral'
          }`}>
            {isBullish ? <TrendingUp className="w-3.5 h-3.5" /> : isBearish ? <TrendingDown className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
            <span>{forecast.direction}</span>
          </div>
        </div>
      </div>

      {/* Forecast Chart */}
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="3 3" opacity={0.4} />
            <XAxis
              dataKey="label"
              stroke="var(--text-muted)"
              tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
              tickLine={{ stroke: 'var(--border-subtle)' }}
            />
            <YAxis
              stroke="var(--text-muted)"
              tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
              tickLine={{ stroke: 'var(--border-subtle)' }}
              orientation="right"
              domain={['auto', 'auto']}
              tickFormatter={(v) => `₹${Number(v).toLocaleString('en-IN')}`}
            />
            <Tooltip
              formatter={(val, name) => [
                `₹${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`,
                name === 'actualClose' ? 'Historical Close' : name === 'forecastPrice' ? 'Projected Forecast' : name
              ]}
              contentStyle={{
                backgroundColor: 'var(--bg-surface)',
                borderColor: 'var(--border-subtle)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--text-primary)',
                borderRadius: '4px',
              }}
            />

            {/* Confidence Band */}
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="var(--accent-brand)"
              fillOpacity={0.12}
              isAnimationActive={false}
            />

            {/* Historical Close */}
            <Line
              type="monotone"
              dataKey="actualClose"
              stroke="var(--text-primary)"
              strokeWidth={2}
              dot={{ r: 2, fill: 'var(--text-primary)' }}
              isAnimationActive={false}
            />

            {/* 5D Forecast Projected Line (Dashed for distinct accessibility) */}
            <Line
              type="monotone"
              dataKey="forecastPrice"
              stroke="var(--accent-brand)"
              strokeWidth={2.2}
              strokeDasharray="6 3"
              dot={{ r: 3, fill: 'var(--accent-brand)' }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 pt-2 border-t border-subtle flex items-center justify-between text-[11px] font-mono text-muted">
        <span>Confidence Range (68% ±1σ):</span>
        <span className="text-primary font-medium">
          {forecast.confidence_lower_pct >= 0 ? '+' : ''}{forecast.confidence_lower_pct?.toFixed(2)}% to{' '}
          {forecast.confidence_upper_pct >= 0 ? '+' : ''}{forecast.confidence_upper_pct?.toFixed(2)}%
        </span>
      </div>
    </div>
  );
}
