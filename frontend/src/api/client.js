/**
 * MarketPulse AI API Client.
 * Handles requests to FastAPI backend with proxy support and structured error handling.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let errorMsg = `API Error ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson && errorJson.detail) {
          errorMsg = errorJson.detail;
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }

    return await response.json();
  } catch (err) {
    console.error(`Fetch failed for ${url}:`, err);
    throw err;
  }
}

export const api = {
  /**
   * Fetches all 8 sectors leaderboard with current health and forecast
   */
  getSectors: () => fetchJson('/sectors'),

  /**
   * Fetches detailed history, forecast, and SHAP drivers for a specific sector
   */
  getSectorDetail: (sectorKey, lookbackDays = 250) =>
    fetchJson(`/sectors/${encodeURIComponent(sectorKey)}?lookback_days=${lookbackDays}`),

  /**
   * Fetches 5-day regression forecast for a specific sector
   */
  getForecast: (sectorKey) =>
    fetchJson(`/forecast/${encodeURIComponent(sectorKey)}`),

  /**
   * Fetches health classification and SHAP feature drivers for a specific sector
   */
  getHealth: (sectorKey) =>
    fetchJson(`/health/${encodeURIComponent(sectorKey)}`),

  /**
   * Fetches full sector rotation backtest metrics, trade logs, and equity curves
   */
  getBacktest: () => fetchJson('/backtest'),
};
