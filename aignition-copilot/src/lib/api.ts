/**
 * AIgnition — Backend API Service Layer
 *
 * All calls to the FastAPI backend go through this file.
 * The base URL reads from the VITE_API_URL env variable (defaults to localhost:8000).
 *
 * Usage:
 *   import { api } from "@/lib/api";
 *   const result = await api.upload(file);
 *   const dashboard = await api.dashboard(result.upload_id);
 */

const BASE_URL =
  (typeof import.meta !== "undefined" && (import.meta as any).env?.VITE_API_URL) ||
  "http://localhost:8000/api/v1";

// ─────────────────────────────────────────────────────────────────────────────
// Types — mirror the Pydantic response models
// ─────────────────────────────────────────────────────────────────────────────

export interface UploadResponse {
  upload_id: string;
  filename: string;
  rows: number;
  columns: string[];
  column_count: number;
  platform_detected: string;
  status: "success" | "error";
  message: string;
}

export interface ValidationIssue {
  row_indices: number[];
  count: number;
  examples: string[];
}

export interface ValidateStep {
  label: string;
  detail: string;
  passed: boolean;
}

export interface ValidateResponse {
  upload_id: string;
  quality_score: number;
  passed: boolean;
  duplicates: ValidationIssue;
  missing_campaigns: ValidationIssue;
  missing_values: ValidationIssue;
  invalid_roas: ValidationIssue;
  revenue_spikes: ValidationIssue;
  invalid_dates: ValidationIssue;
  negative_revenue: ValidationIssue;
  warnings: string[];
  steps: ValidateStep[];
}

export interface ForecastPoint {
  date: string;
  p10: number;
  p50: number;
  p90: number;
  actual?: number | null;
}

export interface RevenueForecast {
  expected: number;
  uplift_pct: number;
  p10: number;
  p50: number;
  p90: number;
  confidence: number;
  mape: number;
  rmse: number;
}

export interface ROASForecast {
  expected: number;
  p10: number;
  p50: number;
  p90: number;
}

export interface ChannelForecast {
  channel: string;
  spend: number;
  revenue: number;
  roas: number;
  current_pct: number;
  optimized_pct: number;
  color: string;
}

export interface CampaignForecast {
  campaign: string;
  spend: number;
  revenue: number;
  roas: number;
}

export interface ForecastResponse {
  upload_id: string;
  is_ml: boolean;
  revenue_forecast: RevenueForecast;
  roas_forecast: ROASForecast;
  series: ForecastPoint[];
  channel_forecast: ChannelForecast[];
  campaign_forecast: CampaignForecast[];
}

export interface ChannelAllocation {
  channel: string;
  current_pct: number;
  optimized_pct: number;
  current_budget: number;
  optimized_budget: number;
  delta_pct: number;
  roas: number;
  color: string;
}

export interface OptimizerResponse {
  upload_id: string;
  total_budget: number;
  google_budget: number;
  meta_budget: number;
  microsoft_budget: number;
  other_budgets: Record<string, number>;
  expected_revenue: number;
  expected_roas: number;
  estimated_uplift_pct: number;
  channels: ChannelAllocation[];
  strategy: Record<string, unknown>;
}

export type RiskSeverity = "healthy" | "watch" | "risk";

export interface RiskItem {
  id: string;
  title: string;
  severity: RiskSeverity;
  description: string;
  metric: string;
  category: string;
}

export interface RisksResponse {
  upload_id: string;
  risk_count: number;
  watch_count: number;
  healthy_count: number;
  risks: RiskItem[];
}

export interface SummaryResponse {
  upload_id: string;
  is_llm: boolean;
  executive_summary: string;
  recommendations: string[];
  key_drivers: string[];
  confidence_explanation: string;
  risk_explanation: string;
}

export interface DashboardResponse {
  upload_id: string;
  forecast: ForecastResponse;
  channels: ChannelAllocation[];
  campaigns: CampaignForecast[];
  optimizer: OptimizerResponse;
  risks: RiskItem[];
  summary: SummaryResponse;
}

// ─────────────────────────────────────────────────────────────────────────────
// Core fetch wrapper
// ─────────────────────────────────────────────────────────────────────────────

class APIError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "APIError";
  }
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new APIError(res.status, detail);
  }

  // For binary responses (PDF, CSV) — caller must handle raw Response
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/pdf") || ct.includes("text/csv")) {
    return res as unknown as T;
  }

  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────────────────────────────────────
// API methods
// ─────────────────────────────────────────────────────────────────────────────

export const api = {
  /**
   * Upload a CSV file. Returns upload_id used by all other endpoints.
   */
  async upload(file: File, source?: string): Promise<UploadResponse> {
    const form = new FormData();
    form.append("file", file);
    if (source) form.append("source", source);
    return request<UploadResponse>("/upload", { method: "POST", body: form });
  },

  /**
   * Run 7 data-quality checks on an uploaded CSV.
   */
  async validate(uploadId: string): Promise<ValidateResponse> {
    return request<ValidateResponse>("/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: uploadId }),
    });
  },

  /**
   * Generate a probabilistic revenue and ROAS forecast.
   */
  async forecast(uploadId: string, horizonDays = 30): Promise<ForecastResponse> {
    return request<ForecastResponse>("/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: uploadId, horizon_days: horizonDays }),
    });
  },

  /**
   * Optimise budget allocation across channels.
   */
  async optimize(
    uploadId: string,
    totalBudget: number,
    opts?: { minChannelPct?: number; maxChannelPct?: number; roasFloor?: number },
  ): Promise<OptimizerResponse> {
    return request<OptimizerResponse>("/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        upload_id: uploadId,
        total_budget: totalBudget,
        min_channel_pct: opts?.minChannelPct ?? 3,
        max_channel_pct: opts?.maxChannelPct ?? 40,
        roas_floor: opts?.roasFloor ?? 2.0,
      }),
    });
  },

  /**
   * Detect risk signals in the dataset.
   */
  async risks(uploadId: string): Promise<RisksResponse> {
    return request<RisksResponse>("/risks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: uploadId }),
    });
  },

  /**
   * Generate an executive summary (LLM or template fallback).
   */
  async summary(
    uploadId: string,
    opts?: { forecast?: unknown; optimizer?: unknown; risks?: unknown[] },
  ): Promise<SummaryResponse> {
    return request<SummaryResponse>("/summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        upload_id: uploadId,
        forecast: opts?.forecast,
        optimizer: opts?.optimizer,
        risks: opts?.risks,
      }),
    });
  },

  /**
   * Unified dashboard endpoint — returns all data in one call.
   */
  async dashboard(
    uploadId: string,
    opts?: { totalBudget?: number; horizonDays?: number },
  ): Promise<DashboardResponse> {
    const params = new URLSearchParams({
      upload_id: uploadId,
      total_budget: String(opts?.totalBudget ?? 420000),
      horizon_days: String(opts?.horizonDays ?? 30),
    });
    return request<DashboardResponse>(`/dashboard?${params}`);
  },

  /**
   * Download a report file. Returns a Blob URL for triggering download.
   */
  async downloadReport(
    uploadId: string,
    format: "csv" | "pdf" = "pdf",
    totalBudget = 420000,
  ): Promise<{ url: string; filename: string }> {
    const params = new URLSearchParams({
      upload_id: uploadId,
      format,
      total_budget: String(totalBudget),
    });
    const res = await fetch(`${BASE_URL}/report?${params}`);
    if (!res.ok) {
      throw new APIError(res.status, `Report download failed: HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    return { url, filename: `aignition-report-${uploadId}.${format}` };
  },

  /**
   * Health check — useful for connectivity testing.
   */
  async health(): Promise<{ status: string; version: string }> {
    return fetch(`${BASE_URL.replace("/api/v1", "")}/health`).then((r) => r.json());
  },
};

export { APIError };
export default api;
