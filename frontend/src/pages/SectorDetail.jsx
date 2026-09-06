import React, { useEffect, useState } from 'react';
import { ArrowLeft, RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import HealthBadge from '../components/HealthBadge';
import PriceChart from '../components/PriceChart';
import ForecastChart from '../components/ForecastChart';
import ShapDrivers from '../components/ShapDrivers';

export default function SectorDetail({ sectorKey, onBack, onSelectSector, allSectors = [] }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lookbackDays, setLookbackDays] = useState(250);

  useEffect(() => {
    if (!sectorKey) return;
    let isMounted = true;
    setLoading(true);
    setError(null);

    api
      .getSectorDetail(sectorKey, lookbackDays)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load sector details');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [sectorKey, lookbackDays]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-6 h-6 text-brand animate-spin" />
        <span className="text-xs font-mono text-muted">Computing indicators & SHAP attributions for {sectorKey}...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-surface border border-signal-avoid/40 rounded p-6 text-center space-y-4">
          <AlertCircle className="w-8 h-8 text-signal-avoid mx-auto" />
          <h2 className="font-display text-lg font-bold text-primary">Could not load sector data</h2>
          <p className="text-xs font-mono text-muted">{error}</p>
          <button
            onClick={onBack}
            className="px-4 py-2 rounded bg-base border border-subtle text-xs font-mono text-primary hover:bg-surface-hover cursor-pointer"
          >
            ← Back to Leaderboard
          </button>
        </div>
      </div>
    );
  }

  const latestPoint = data.price_history && data.price_history.length > 0
    ? data.price_history[data.price_history.length - 1]
    : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* 1. Sector Switcher Tabs */}
      <div className="flex items-center justify-between gap-4 overflow-x-auto pb-2 border-b border-subtle">
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={onBack}
            className="p-1.5 rounded hover:bg-surface border border-subtle text-muted hover:text-primary transition-colors cursor-pointer mr-2"
            title="Back to Leaderboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          
          {allSectors.map((s) => (
            <button
              key={s.sector}
              onClick={() => onSelectSector(s.sector)}
              className={`px-3 py-1.5 rounded text-xs font-mono transition-colors cursor-pointer shrink-0 ${
                s.sector === sectorKey
                  ? 'bg-brand-subtle text-brand border border-brand/40 font-semibold'
                  : 'bg-surface text-muted hover:text-primary border border-subtle'
              }`}
            >
              {s.sector}
            </button>
          ))}
        </div>

        {/* Lookback Filter */}
        <div className="flex items-center gap-1 text-xs font-mono text-muted shrink-0">
          <span className="hidden sm:inline">Range:</span>
          {[125, 250, 500].map((days) => (
            <button
              key={days}
              onClick={() => setLookbackDays(days)}
              className={`px-2 py-0.5 rounded border text-[11px] cursor-pointer ${
                lookbackDays === days
                  ? 'bg-brand-subtle text-brand border-brand/40 font-semibold'
                  : 'bg-surface text-muted border-subtle hover:text-primary'
              }`}
            >
              {days === 125 ? '6M' : days === 250 ? '1Y' : '2Y'}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Sector Header Card */}
      <div className="bg-surface border border-subtle rounded p-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="font-display text-2xl font-bold text-primary">{data.sector_name}</h1>
              <HealthBadge label={data.health_label} size="md" />
            </div>
            <p className="text-xs text-muted font-body mt-1 max-w-2xl">{data.description}</p>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs font-mono bg-base p-3 rounded border border-subtle">
            <div>
              <div className="text-[10px] text-muted uppercase">Latest Close</div>
              <div className="text-base font-bold text-primary">₹{data.latest_close.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
            </div>
            <div className="h-6 w-px bg-subtle" />
            <div>
              <div className="text-[10px] text-muted uppercase">20D Change</div>
              <div className={`text-sm font-semibold ${data.change_20d_pct >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                {data.change_20d_pct >= 0 ? '+' : ''}{data.change_20d_pct.toFixed(2)}%
              </div>
            </div>
            <div className="h-6 w-px bg-subtle" />
            <div>
              <div className="text-[10px] text-muted uppercase">5D Forecast</div>
              <div className={`text-sm font-semibold ${data.forecast?.predicted_return_pct >= 0 ? 'text-signal-buy' : 'text-signal-avoid'}`}>
                {data.forecast?.predicted_return_pct >= 0 ? '+' : ''}{data.forecast?.predicted_return_pct?.toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Price Action & Indicators Chart */}
        <div className="lg:col-span-8 space-y-6">
          <PriceChart
            priceHistory={data.price_history}
            sectorName={data.sector_name}
          />

          {/* SHAP Attribution Panel */}
          <ShapDrivers
            drivers={data.top_drivers}
            healthLabel={data.health_label}
          />
        </div>

        {/* Right Column: 5D Forecast Cone & Technical Indicators Card */}
        <div className="lg:col-span-4 space-y-6">
          <ForecastChart
            forecast={data.forecast}
            latestClose={data.latest_close}
            recentHistory={data.price_history}
          />

          {/* Technical Diagnostics */}
          {latestPoint && (
            <div className="bg-surface border border-subtle rounded p-4 space-y-3">
              <h3 className="font-display text-sm font-bold text-primary pb-2 border-b border-subtle">
                Technical Diagnostics
              </h3>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-subtle/50">
                  <span className="text-muted">14-Day RSI:</span>
                  <span className={latestPoint.rsi_14 > 70 ? 'text-signal-avoid font-semibold' : latestPoint.rsi_14 < 30 ? 'text-signal-buy font-semibold' : 'text-primary'}>
                    {latestPoint.rsi_14 || 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between py-1 border-b border-subtle/50">
                  <span className="text-muted">Price vs 20-Day EMA:</span>
                  <span className={latestPoint.close >= latestPoint.ema_20 ? 'text-signal-buy font-semibold' : 'text-signal-avoid font-semibold'}>
                    {latestPoint.ema_20 ? `${(((latestPoint.close / latestPoint.ema_20) - 1) * 100).toFixed(2)}%` : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between py-1 border-b border-subtle/50">
                  <span className="text-muted">Price vs 50-Day SMA:</span>
                  <span className={latestPoint.close >= latestPoint.sma_50 ? 'text-signal-buy font-semibold' : 'text-signal-avoid font-semibold'}>
                    {latestPoint.sma_50 ? `${(((latestPoint.close / latestPoint.sma_50) - 1) * 100).toFixed(2)}%` : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between py-1 border-b border-subtle/50">
                  <span className="text-muted">MACD Histogram:</span>
                  <span className={latestPoint.macd_hist >= 0 ? 'text-signal-buy font-semibold' : 'text-signal-avoid font-semibold'}>
                    {latestPoint.macd_hist ? (latestPoint.macd_hist > 0 ? `+${latestPoint.macd_hist.toFixed(2)}` : latestPoint.macd_hist.toFixed(2)) : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between py-1">
                  <span className="text-muted">As of Session:</span>
                  <span className="text-primary">{latestPoint.date}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
