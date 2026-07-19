import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState } from "react";
import {
  UploadCloud, FileSpreadsheet, Sparkles, ArrowRight,
  ShieldCheck, LineChart, Wand2, CheckCircle2, TrendingUp,
  Sliders, GitCompare, MessageSquare, AlertTriangle, FileDown,
} from "lucide-react";
import { SoftCard } from "@/components/ai/Card";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AIgnition — AI Marketing Decision Copilot" },
      { name: "description", content: "Upload your marketing data and let AIgnition forecast, optimize and explain your next move." },
    ],
  }),
  component: Landing,
});

const STEPS = [
  { icon: UploadCloud, t: "Upload", d: "Drop your marketing CSV — spend & revenue by channel." },
  { icon: CheckCircle2, t: "Validate", d: "Automated data-quality score & anomaly checks." },
  { icon: TrendingUp, t: "Forecast", d: "P10 / P50 / P90 probabilistic revenue outlook." },
  { icon: Sliders, t: "Optimize", d: "AI budget reallocation across every channel." },
  { icon: GitCompare, t: "Compare", d: "Side-by-side scenarios: baseline vs optimized vs aggressive." },
  { icon: AlertTriangle, t: "Detect risks", d: "Fatigue, saturation and data-drift alerts before they hurt." },
  { icon: MessageSquare, t: "Explain", d: "Chat with the AI copilot to interrogate the plan." },
  { icon: FileDown, t: "Export", d: "One-click CMO-ready PDF & CSV report." },
];

function Landing() {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const navigate = useNavigate();

  function handleFile(f?: File | null) {
    if (!f) return;
    setFileName(f.name);
    setTimeout(() => navigate({ to: "/validate" }), 600);
  }

  return (
    <div>
      {/* Hero — description of what AIgnition is */}
      <section className="mx-auto max-w-3xl text-center">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 rounded-full border border-border bg-white/70 px-3 py-1 text-xs font-medium text-muted-foreground">
          <Sparkles className="h-3.5 w-3.5 text-[color:var(--brand)]" />
          AI Marketing Decision Copilot
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="mt-4 text-4xl font-extrabold leading-[1.05] tracking-tight md:text-6xl"
        >
          Your AI Marketing<br />
          <span className="text-gradient-brand">Decision Copilot</span>
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}
          className="mx-auto mt-5 max-w-2xl text-base text-muted-foreground md:text-lg">
          Beyond forecasting. AIgnition validates your marketing data, projects revenue with
          confidence bands, optimizes budget across channels, simulates what-ifs, flags risks
          and explains the recommendation — so you can decide with conviction, not gut feel.
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-3 text-xs">
          {[
            { icon: ShieldCheck, label: "Data-quality guardrails" },
            { icon: LineChart, label: "Probabilistic forecasts" },
            { icon: Wand2, label: "AI explanations" },
          ].map((f) => (
            <div key={f.label} className="flex items-center gap-2 rounded-xl border border-border bg-white/70 px-3 py-2">
              <f.icon className="h-4 w-4 text-[color:var(--brand)]" />
              <span className="font-medium">{f.label}</span>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Upload — main CTA */}
      <motion.section id="upload"
        initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.35 }}
        className="mx-auto mt-12 max-w-2xl md:mt-16"
      >
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files?.[0]); }}
          className={`relative overflow-hidden rounded-3xl border-2 border-dashed p-8 md:p-10 transition-all ${
            dragOver ? "border-[color:var(--brand)] bg-white shadow-[var(--shadow-lift)]" : "border-border bg-white/70"
          }`}
        >
          <motion.div
            animate={{ opacity: dragOver ? 1 : 0.6, scale: dragOver ? 1.02 : 1 }}
            className="pointer-events-none absolute inset-0 -z-10 gradient-brand opacity-[0.06]"
          />
          <div className="flex flex-col items-center text-center">
            <motion.div
              animate={{ y: dragOver ? -4 : 0 }}
              className="grid h-16 w-16 place-items-center rounded-2xl gradient-brand text-white shadow-[var(--shadow-lift)]"
            >
              <UploadCloud className="h-7 w-7" />
            </motion.div>
            <h3 className="mt-4 text-lg font-semibold">Drop your marketing CSV to start</h3>
            <p className="mt-1 max-w-md text-sm text-muted-foreground">
              Daily spend & revenue by channel. We'll auto-detect schema and walk you through the full workflow.
            </p>
            <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
              <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-border bg-white px-4 py-2 text-sm font-medium shadow-[var(--shadow-soft)] hover:shadow-[var(--shadow-lift)]">
                <FileSpreadsheet className="h-4 w-4 text-[color:var(--brand)]" />
                Choose file
                <input type="file" accept=".csv" className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
              </label>
              <button
                onClick={() => navigate({ to: "/validate" })}
                className="group inline-flex items-center gap-2 rounded-xl gradient-brand px-5 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-lift)] transition hover:scale-[1.03]"
              >
                Try sample dataset
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </button>
            </div>
            {fileName && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-3 text-xs text-[color:var(--success)]">
                Loaded {fileName} — validating…
              </motion.p>
            )}
          </div>
        </div>
      </motion.section>

      {/* 8-step workflow */}
      <section className="mt-16 md:mt-24">
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--brand)]">The workflow</div>
          <h2 className="mt-2 text-2xl font-bold tracking-tight md:text-3xl">
            From messy CSV to a decision, in 8 steps
          </h2>
          <p className="mt-2 text-sm text-muted-foreground md:text-base">
            AIgnition guides you through the full loop — not just a chart.
          </p>
        </div>

        <div className="mt-8 grid gap-4 md:mt-10 md:grid-cols-4">
          {STEPS.map((s, i) => (
            <SoftCard key={s.t} delay={i * 0.06}>
              <div className="flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-xl gradient-brand text-white">
                  <s.icon className="h-4 w-4" />
                </span>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Step {i + 1}
                </div>
              </div>
              <div className="mt-3 text-lg font-semibold">{s.t}</div>
              <div className="mt-1 text-sm text-muted-foreground">{s.d}</div>
            </SoftCard>
          ))}
        </div>

        <div className="mt-10 flex justify-center">
          <button
            onClick={() => navigate({ to: "/validate" })}
            className="group inline-flex items-center gap-2 rounded-xl gradient-brand px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-lift)] transition hover:scale-[1.03]"
          >
            Start the workflow with sample data
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </button>
        </div>
      </section>
    </div>
  );
}
