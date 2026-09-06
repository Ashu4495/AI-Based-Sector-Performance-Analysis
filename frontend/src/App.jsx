import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import SectorDetail from './pages/SectorDetail';
import Backtest from './pages/Backtest';
import { RefreshCw, AlertCircle } from 'lucide-react';

export default function App() {
  const [activePage, setActivePage] = useState('landing');
  const [selectedSector, setSelectedSector] = useState('IT');
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSectors = () => {
    setLoading(true);
    setError(null);
    api
      .getSectors()
      .then((res) => {
        setSectors(res.sectors || []);
        if (res.sectors && res.sectors.length > 0 && !selectedSector) {
          setSelectedSector(res.sectors[0].sector);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch sectors from MarketPulse AI backend');
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchSectors();
  }, []);

  const handleSelectSector = (sectorKey) => {
    setSelectedSector(sectorKey);
    setActivePage('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-base text-primary flex flex-col font-body">
      {/* Top Navigation */}
      <Navbar
        activePage={activePage}
        setActivePage={(page) => {
          setActivePage(page);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        selectedSector={selectedSector}
      />

      {/* Main Content Area */}
      <main className="flex-1 w-full">
        {loading ? (
          <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
            <RefreshCw className="w-8 h-8 text-brand animate-spin" />
            <div className="font-mono text-xs text-muted">Connecting to MarketPulse AI Engine...</div>
          </div>
        ) : error ? (
          <div className="max-w-2xl mx-auto px-4 py-16 text-center">
            <div className="bg-surface border border-signal-avoid/40 rounded p-8 space-y-4 shadow-sm">
              <AlertCircle className="w-10 h-10 text-signal-avoid mx-auto" />
              <h2 className="font-display text-xl font-bold text-primary">Backend API Connection Error</h2>
              <p className="text-xs font-mono text-muted leading-relaxed">{error}</p>
              <button
                onClick={fetchSectors}
                className="px-4 py-2 rounded bg-brand-subtle text-brand border border-brand/40 font-mono text-xs font-semibold hover:bg-brand-subtle/80 cursor-pointer"
              >
                Retry Connection
              </button>
            </div>
          </div>
        ) : (
          <>
            {activePage === 'landing' && (
              <Landing
                sectors={sectors}
                onExplore={() => setActivePage('dashboard')}
                onSelectSector={handleSelectSector}
              />
            )}

            {activePage === 'dashboard' && (
              <Dashboard
                sectors={sectors}
                onSelectSector={handleSelectSector}
                onOpenBacktest={() => setActivePage('backtest')}
                selectedSector={selectedSector}
              />
            )}

            {activePage === 'detail' && (
              <SectorDetail
                sectorKey={selectedSector}
                onBack={() => setActivePage('dashboard')}
                onSelectSector={(s) => setSelectedSector(s)}
                allSectors={sectors}
              />
            )}

            {activePage === 'backtest' && <Backtest />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full bg-surface border-t border-subtle py-6 mt-12 text-xs font-mono text-muted">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 text-center sm:text-left">
            <div className="flex items-center gap-2">
              <img src="/logo.png" alt="Logo" className="w-5 h-5 object-contain" />
              <span className="font-display font-bold text-primary text-sm">MarketPluse AI</span>
            </div>
            <span className="hidden sm:inline text-subtle">|</span>
            <span className="text-[10px] tracking-wide">SMART INSIGHTS • BETTER TRADES • BRIGHTER TOMORROW</span>
          </div>
          <div className="flex items-center gap-4 text-[10px]">
            <span>Data: yfinance</span>
            <span className="hidden md:inline">Models: Ridge Regression + RandomForest + TreeSHAP</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

