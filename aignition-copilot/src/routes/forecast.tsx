import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { AlertTriangle, ArrowRight, TrendingUp, Target, Gauge } from "lucide-react";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { AnimatedNumber } from "@/components/ai/AnimatedNumber";
import { ConfidenceGauge } from "@/components/ai/ConfidenceGauge";
import { ForecastChart } from "@/components/ai/ForecastChart";
import { generateForecast, kpis } from "@/lib/mock-data";

export const Route = createFileRoute("/forecast")({
  head: () => ({ meta: [{ title: "Forecast — AIgnition" }, { name: "description", content: "Probabilistic revenue forecast with P10/P50/P90 confidence bands." }] }),
  component: Forecast,
});

function Forecast() {
  const data = useMemo(() => generateForecast(60), []);
  const [showActual, setShowActual] = useState(true);

  return (
    <div>
      <PageHeader eyebrow="Step 2" title="Forecast dashboard"
        subtitle="Probabilistic outlook with uncertainty bands and drift monitoring."
        right={
          <Link to="/optimizer" className="inline-flex items-center gap-2 rounded-xl gradient-brand px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-lift)] hover:scale-[1.03]">
            Optimize budget <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        className="mb-5 flex items-center gap-3 rounded-2xl border border-[color:var(--warning)]/30 bg-[color:var(--warning)]/10 p-4">
        <span className="pulse-soft grid h-8 w-8 place-items-center rounded-full bg-[color:var(--warning)]/20 text-[color:var(--warning)]">
          <AlertTriangle className="h-4 w-4" />
        </span>
        <div className="flex-1">
          <div className="text-sm font-semibold">Mild data drift detected</div>
          <div className="text-xs text-muted-foreground">Distribution of Meta CPMs has shifted 8% over the past 7 days. Retraining recommended within 3 days.</div>
        </div>
        <button className="rounded-lg border border-border bg-white px-3 py-1.5 text-xs font-medium hover:shadow-[var(--shadow-soft)]">Retrain</button>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-4">
        <SoftCard delay={0.0}>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <TrendingUp className="h-3.5 w-3.5 text-[color:var(--brand)]" /> Expected Revenue
          </div>
          <div className="mt-2 text-2xl font-bold">
            $<AnimatedNumber value={kpis.expectedRevenue} />
          </div>
          <div className="mt-1 text-xs text-[color:var(--success)]">+<AnimatedNumber value={kpis.uplift} format={(n) => n.toFixed(1)} />% vs baseline</div>
        </SoftCard>
        <SoftCard delay={0.08}>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Target className="h-3.5 w-3.5 text-[color:var(--brand)]" /> ROAS
          </div>
          <div className="mt-2 text-2xl font-bold"><AnimatedNumber value={kpis.roas} format={(n) => n.toFixed(2)} />x</div>
          <div className="mt-1 text-xs text-muted-foreground">Blended, next 30 days</div>
        </SoftCard>
        <SoftCard delay={0.16}>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Gauge className="h-3.5 w-3.5 text-[color:var(--brand)]" /> Forecast Accuracy
          </div>
          <div className="mt-2 text-2xl font-bold">
            <AnimatedNumber value={100 - kpis.mape} format={(n) => n.toFixed(1)} />%
          </div>
          <div className="mt-1 text-xs text-muted-foreground" title="MAPE / RMSE on hold-out">
            MAPE {kpis.mape}% · RMSE ${kpis.rmse.toLocaleString()}
          </div>
        </SoftCard>
        <SoftCard delay={0.24} className="flex items-center gap-4">
          <ConfidenceGauge value={kpis.confidence} size={100} />
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Confidence</div>
            <div className="mt-1 text-xs text-muted-foreground">Ensemble agreement across 5 models</div>
          </div>
        </SoftCard>
      </div>

      <SoftCard className="mt-6" delay={0.3}>
        <div className="mb-3 flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">Revenue forecast · P10 / P50 / P90</div>
            <div className="text-xs text-muted-foreground">Last 30 days actual + 30 day forward projection</div>
          </div>
          <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-white px-3 py-1.5 text-xs font-medium">
            <input type="checkbox" checked={showActual} onChange={(e) => setShowActual(e.target.checked)} className="accent-[color:var(--brand)]" />
            Show actual vs forecast
          </label>
        </div>
        <ForecastChart data={data} showActual={showActual} />
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full gradient-brand" /> P50 median</span>
          <span className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-[color:var(--brand-2)]/40" /> P10–P90 uncertainty</span>
          <span className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-[color:var(--success)]" /> Actual (dashed)</span>
        </div>
      </SoftCard>
    </div>
  );
}
