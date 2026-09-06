import React from 'react';
import { Activity, BarChart3, LineChart, Compass, ShieldCheck } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function Navbar({ activePage, setActivePage, selectedSector }) {
  const navItems = [
    { id: 'landing', label: 'Overview', icon: Compass },
    { id: 'dashboard', label: 'Sector Leaderboard', icon: BarChart3 },
    { id: 'detail', label: selectedSector ? `${selectedSector} Deep Dive` : 'Sector Detail', icon: LineChart },
    { id: 'backtest', label: 'Rotation Backtest', icon: Activity },
  ];

  return (
    <header className="w-full bg-surface border-b border-subtle sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* Left: Brand */}
        <div
          onClick={() => setActivePage('landing')}
          className="flex items-center gap-3 cursor-pointer select-none group"
        >
          <div className="w-7 h-7 rounded border border-brand bg-brand-subtle flex items-center justify-center">
            <span className="font-display font-bold text-base text-brand">S</span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-display text-lg font-bold tracking-tight text-primary">SectorAI</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface border border-subtle text-muted">
                NSE ML
              </span>
            </div>
          </div>
        </div>

        {/* Center: Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-brand-subtle text-brand border border-brand/30'
                    : 'text-muted hover:text-primary hover:bg-surface-hover border border-transparent'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right: Status & Theme Toggle */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-mono text-muted">
            <span className="w-2 h-2 rounded-full bg-signal-buy animate-pulse" />
            <span>yfinance · 8 Sectors</span>
          </div>
          <div className="h-4 w-px bg-subtle hidden sm:block" />
          <ThemeToggle />
        </div>
      </div>

      {/* Mobile Sub-Navbar */}
      <div className="md:hidden flex items-center justify-around border-t border-subtle px-2 py-1.5 bg-surface text-xs font-mono overflow-x-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded shrink-0 ${
                isActive
                  ? 'bg-brand-subtle text-brand font-semibold'
                  : 'text-muted'
              }`}
            >
              <Icon className="w-3 h-3" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
