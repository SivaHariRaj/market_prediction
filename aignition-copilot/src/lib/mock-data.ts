// Mock data for AIgnition demo
export type ForecastPoint = {
  date: string;
  actual?: number;
  p10: number;
  p50: number;
  p90: number;
};

function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

export function generateForecast(days = 60, seed = 42): ForecastPoint[] {
  const rand = seeded(seed);
  const out: ForecastPoint[] = [];
  const start = new Date();
  start.setDate(start.getDate() - 30);
  let base = 42000;
  for (let i = 0; i < days; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    const trend = i * 220;
    const season = Math.sin((i / 7) * Math.PI) * 4200;
    const noise = (rand() - 0.5) * 3200;
    const p50 = Math.max(0, base + trend + season + noise);
    const spread = 4200 + i * 90;
    const point: ForecastPoint = {
      date: d.toISOString().slice(5, 10),
      p10: Math.max(0, p50 - spread),
      p50,
      p90: p50 + spread,
    };
    if (i < 30) point.actual = p50 + (rand() - 0.5) * 2400;
    out.push(point);
  }
  return out;
}

export type Channel = {
  name: string;
  current: number;
  optimized: number;
  roas: number;
  color: string;
};

export const channels: Channel[] = [
  { name: "Google Search", current: 32, optimized: 38, roas: 4.2, color: "var(--brand)" },
  { name: "Meta Ads", current: 28, optimized: 24, roas: 3.1, color: "var(--brand-2)" },
  { name: "TikTok", current: 14, optimized: 18, roas: 3.8, color: "var(--success)" },
  { name: "YouTube", current: 12, optimized: 11, roas: 2.9, color: "var(--warning)" },
  { name: "Programmatic", current: 9, optimized: 6, roas: 1.8, color: "var(--danger)" },
  { name: "Affiliate", current: 5, optimized: 3, roas: 2.4, color: "oklch(0.55 0.12 240)" },
];

export type RiskItem = {
  id: string;
  title: string;
  severity: "healthy" | "watch" | "risk";
  description: string;
  metric: string;
};

export const risks: RiskItem[] = [
  { id: "sat", title: "Campaign Saturation", severity: "watch", description: "Google Search returns diminishing at >$38k/wk.", metric: "-8% marginal ROAS" },
  { id: "fatigue", title: "Creative Fatigue", severity: "risk", description: "Meta CTR down 22% over last 14 days on top creatives.", metric: "CTR 0.9%" },
  { id: "ctr", title: "CTR Decline", severity: "watch", description: "TikTok CTR trending down for younger cohort.", metric: "-6% WoW" },
  { id: "conv", title: "Conversion Drop", severity: "healthy", description: "Checkout conversion stable across channels.", metric: "3.4%" },
  { id: "cpa", title: "CPA Spike", severity: "risk", description: "Programmatic CPA up 41% — likely inventory quality.", metric: "$62 CPA" },
  { id: "track", title: "Tracking Anomaly", severity: "watch", description: "Gap detected in UTM ingestion Nov 3–4.", metric: "2 days" },
  { id: "conc", title: "Budget Concentration", severity: "healthy", description: "No single channel exceeds 40% of spend.", metric: "38% max" },
  { id: "seas", title: "Seasonal Shift", severity: "watch", description: "Holiday demand curve starts ~10 days earlier YoY.", metric: "+10d" },
];

export const validationSteps = [
  { label: "Schema check", detail: "12 columns, expected format" },
  { label: "Missing values", detail: "0.4% imputed" },
  { label: "Date continuity", detail: "No gaps in 18 months" },
  { label: "Outlier detection", detail: "3 flagged, non-blocking" },
  { label: "Channel normalization", detail: "6 channels mapped" },
  { label: "Currency check", detail: "USD, consistent" },
];

export const kpis = {
  expectedRevenue: 1284000,
  roas: 3.7,
  uplift: 12.4,
  confidence: 87,
  mape: 6.2,
  rmse: 4180,
};
