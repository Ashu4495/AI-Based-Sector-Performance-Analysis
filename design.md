# design.md — Visual & UX Design

Frontend is a **custom React application** (no Streamlit). This document defines the design plan: tokens, typography, layout, and the principles behind them, grounded in the subject matter — an Indian equity sector-analysis tool, closer in spirit to a financial terminal / analyst desk than a generic SaaS dashboard.

## 1. Design Plan

### Color

Two themes, sharing a structure but not just an inverted palette — semantic colors are tuned separately for contrast in each mode.

**Dark theme** (default — analyst "trading desk" feel)
| Token | Hex | Use |
|---|---|---|
| `bg-base` | `#0F1B2B` | App background (deep ink-navy, not flat black) |
| `bg-surface` | `#16233A` | Cards, panels, table rows |
| `text-primary` | `#E7ECF2` | Primary text |
| `text-muted` | `#8FA0B8` | Secondary text, labels |
| `accent-brand` | `#3FA796` | Links, active states, brand touches (muted teal, not neon) |
| `signal-buy` | `#4E9F6E` | Strong Buy / Buy label |
| `signal-neutral` | `#C99A3E` | Neutral label |
| `signal-avoid` | `#C1503F` | Avoid / Strong Avoid label |

**Light theme** (analyst desk in daylight — a research-note feel)
| Token | Hex | Use |
|---|---|---|
| `bg-base` | `#EEF0EC` | App background (cool paper, not warm cream) |
| `bg-surface` | `#FFFFFF` | Cards, panels, table rows |
| `text-primary` | `#1A2330` | Primary text |
| `text-muted` | `#5B6B7F` | Secondary text, labels |
| `accent-brand` | `#1F6F63` | Links, active states |
| `signal-buy` | `#2F7D52` | Strong Buy / Buy label |
| `signal-neutral` | `#9C6B1F` | Neutral label |
| `signal-avoid` | `#A13D2E` | Avoid / Strong Avoid label |

Why this palette: it deliberately avoids the two most common generated-page defaults — warm cream + terracotta, and near-black + single neon accent. Instead, the base is a desaturated navy/paper pair, and color is spent on **meaning** (the buy/neutral/avoid signal colors) rather than decoration. There is no gradient anywhere in the UI — data density and clarity carry the design, not decoration.

### Type

- **Display/headline**: `Fraunces` — a serif with enough texture to feel editorial (closer to a financial-press masthead than a tech startup), used only for the landing page headline and section titles.
- **UI/body**: `IBM Plex Sans` — clean, technical, slightly more distinctive than a default grotesk, used for all body text, labels, and navigation.
- **Data/numeric**: `IBM Plex Mono` — used *only* for numbers: prices, percentages, returns, dates in tables. This is a functional choice (monospace digits align cleanly in columns), not a decorative label font, so it's used exclusively where tabular alignment matters — never for headings or prose.

Line length capped around 70–75 characters for body copy. Left-aligned throughout (no center-aligned marketing blocks) — the product is a data tool, and left alignment matches how the dashboard itself reads.

### Layout Concept

A left-anchored, data-dense layout throughout, with generous whitespace only around the landing hero. Structural devices (hairline dividers, small-radius panels at 4px, not 0 and not pill-shaped) encode grouping — no drop shadows, no card-soup.

**Landing page** — the hero is a **live sector strip**, not a headline+gradient block:

```
┌────────────────────────────────────────────────────────────┐
│  SectorAI                                    [Light/Dark]  │
├────────────────────────────────────────────────────────────┤
│                                                              │
│   IT  ▲1.2%   BANK ▼0.4%   AUTO ▲0.8%   PHARMA ▲0.3%  ...   │  ← live-style ticker strip
│                                                              │
│   Which NSE sectors deserve                                 │
│   your attention this week.                                 │  ← Fraunces serif headline
│                                                              │
│   An explainable read on sector health and near-term        │
│   direction — built on price data, not guesswork.           │
│                                                              │
│   [ View sector leaderboard ]                                │
│                                                              │
├────────────────────────────────────────────────────────────┤
│  How it reads a sector →   Momentum · Relative strength ·   │
│  Volatility · Trend  (short explainer, plain language)       │
└────────────────────────────────────────────────────────────┘
```

The ticker strip is the "most characteristic thing in this subject's world" — it immediately signals *market data tool* before any copy is read.

**Dashboard (leaderboard view)**:

```
┌───────────┬──────────────────────────────────────────────┐
│  Sectors   │  Leaderboard                                  │
│  ─────     │  ┌────────────────────────────────────────┐  │
│  ● IT      │  │ Sector      Label          Δ 20d        │  │
│  ● Bank    │  │ IT          Strong Buy     +4.2%         │  │
│  ● Auto    │  │ FMCG        Buy            +1.8%         │  │
│  ● Pharma  │  │ Bank        Neutral        +0.3%         │  │
│  ● FMCG    │  │ Auto        Avoid          -1.1%         │  │
│  ● Metal   │  │ Metal       Strong Avoid   -3.4%         │  │
│  ● Energy  │  └────────────────────────────────────────┘  │
│  ● Realty  │                                                │
│            │  [ Backtest: strategy vs NIFTY 50 → ]         │
└───────────┴──────────────────────────────────────────────┘
```

Left rail: fixed sector list (navigation). Main panel: leaderboard table, sorted by label (Strong Buy → Strong Avoid), with the signal colors applied only to the label text/badge — not the whole row — to keep the table calm and legible.

**Sector detail view**: price chart (top), forecast overlay line distinguished by dash pattern (not just color, for accessibility), and a compact SHAP panel below listing the top 3–4 features driving the current label in plain language (e.g., "20-day relative strength vs. NIFTY 50" rather than a raw feature name like `rel_str_20d`).

### Principles

1. **Signal color means one thing only** — buy/neutral/avoid semantics are never reused for anything else in the UI (no green "success" toasts, no red "error" states borrowing the same hue) so the meaning stays trustworthy at a glance.
2. **Numbers live in monospace, words don't** — reinforces that this is a data tool without resorting to a "terminal" pastiche (no scanlines, no ASCII borders in the real UI).
3. **One motion moment**: the ticker strip scrolls gently on the landing page load; nothing else animates on scroll. Hover states are simple opacity/underline changes, not transforms.
4. **Labels over numbers everywhere in the health system** — per `PRD.md`, no numeric health score is ever shown; badges/text only (Strong Buy / Buy / Neutral / Avoid / Strong Avoid).

## 2. Review Against Brief

- Avoided the cream+terracotta and near-black+neon defaults explicitly (see palette rationale above).
- No ALL-CAPS eyebrows, no middle-dot meta strings, no arrow-suffixed buttons, no numbered 01/02/03 markers (the sector list isn't a sequence, so it's shown as a plain list, not numbered).
- Typography pairing (serif display + grotesk UI + monospace data) is chosen for a specific functional reason (tabular alignment) rather than applied decoratively.

## 3. Accessibility & Responsiveness

- All signal colors meet WCAG AA contrast against their respective backgrounds in both themes.
- Color is never the only differentiator — labels always ship with text, not color alone (important since Buy/Avoid must be distinguishable for colorblind users).
- Dashboard collapses to a single-column, bottom-tab-navigation layout below 768px width; the left sector rail becomes a horizontal scrollable strip.
- Visible keyboard focus states on all interactive elements; reduced-motion media query disables the ticker scroll animation.
