import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState } from "react";
import { Download, FileText, Sparkles } from "lucide-react";
import jsPDF from "jspdf";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { AnimatedNumber } from "@/components/ai/AnimatedNumber";
import { kpis } from "@/lib/mock-data";

export const Route = createFileRoute("/report")({
  head: () => ({ meta: [{ title: "Executive Report — AIgnition" }, { name: "description", content: "Preview and export a CMO-ready decision report." }] }),
  component: Report,
});

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function buildPdf() {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const W = doc.internal.pageSize.getWidth();
  let y = 56;

  // Header band
  doc.setFillColor(99, 102, 241);
  doc.rect(0, 0, W, 8, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(120);
  doc.text("AIGNITION · DECISION REPORT", 40, y);
  y += 20;
  doc.setFontSize(20);
  doc.setTextColor(20);
  doc.text("Q4 marketing plan — 30-day outlook", 40, y);
  y += 18;
  doc.setFontSize(10);
  doc.setTextColor(120);
  doc.setFont("helvetica", "normal");
  doc.text(`Generated ${new Date().toLocaleDateString()} · Model ensemble v3.2`, 40, y);
  y += 30;

  // KPI blocks
  const kpiRows = [
    ["Expected Revenue", `$${kpis.expectedRevenue.toLocaleString()}`, `+${kpis.uplift}% vs baseline`],
    ["Blended ROAS", `${kpis.roas.toFixed(2)}x`, "next 30 days"],
    ["Confidence", `${kpis.confidence}%`, `MAPE ${kpis.mape}%`],
  ];
  const boxW = (W - 80 - 24) / 3;
  kpiRows.forEach((r, i) => {
    const x = 40 + i * (boxW + 12);
    doc.setDrawColor(226);
    doc.setFillColor(250, 250, 253);
    doc.roundedRect(x, y, boxW, 72, 8, 8, "FD");
    doc.setFontSize(8);
    doc.setTextColor(120);
    doc.setFont("helvetica", "bold");
    doc.text(r[0].toUpperCase(), x + 12, y + 18);
    doc.setFontSize(18);
    doc.setTextColor(20);
    doc.text(r[1], x + 12, y + 42);
    doc.setFontSize(9);
    doc.setTextColor(34, 150, 90);
    doc.setFont("helvetica", "normal");
    doc.text(r[2], x + 12, y + 60);
  });
  y += 96;

  // Recommendation
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(20);
  doc.text("Recommendation", 40, y);
  y += 16;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.setTextColor(60);
  const recText = doc.splitTextToSize(
    "Apply the AI-optimized allocation: shift ~$14k from Programmatic and Affiliate into Google Search and TikTok. Expected revenue lift: $142,000.",
    W - 80,
  );
  doc.text(recText, 40, y);
  y += recText.length * 14 + 18;

  // Risks
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(20);
  doc.text("Top risks", 40, y);
  y += 16;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  const risks = [
    ["#DC2626", "Meta creative fatigue — refresh within 7 days"],
    ["#D97706", "Google Search nearing saturation at $38k/wk"],
    ["#D97706", "Mild data drift on Meta CPMs"],
  ];
  risks.forEach(([color, txt]) => {
    const [r, g, b] = [parseInt(color.slice(1, 3), 16), parseInt(color.slice(3, 5), 16), parseInt(color.slice(5, 7), 16)];
    doc.setFillColor(r, g, b);
    doc.circle(46, y - 3, 3, "F");
    doc.setTextColor(60);
    doc.text(txt, 58, y);
    y += 16;
  });
  y += 12;

  // Executive summary
  doc.setDrawColor(226);
  doc.setFillColor(246, 247, 252);
  doc.roundedRect(40, y, W - 80, 92, 8, 8, "FD");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(120);
  doc.text("EXECUTIVE SUMMARY", 52, y + 20);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.setTextColor(40);
  const summary = doc.splitTextToSize(
    "AIgnition recommends the optimized plan: +12.4% revenue lift at 3.7x blended ROAS, with a single watch-level risk. Aggressive alternatives can capture more revenue but reintroduce fatigue and saturation risks unlikely to be resolved inside the window.",
    W - 104,
  );
  doc.text(summary, 52, y + 40);

  // Footer
  doc.setFontSize(8);
  doc.setTextColor(160);
  doc.text("AIgnition · AI Marketing Decision Copilot", 40, doc.internal.pageSize.getHeight() - 24);

  return doc.output("blob");
}

function buildCsv() {
  const rows: string[][] = [
    ["AIgnition Decision Report"],
    ["Generated", new Date().toISOString()],
    [],
    ["Metric", "Value", "Note"],
    ["Expected Revenue", String(kpis.expectedRevenue), `+${kpis.uplift}% vs baseline`],
    ["Blended ROAS", kpis.roas.toFixed(2), "next 30 days"],
    ["Confidence %", String(kpis.confidence), `MAPE ${kpis.mape}%`],
    [],
    ["Recommendation"],
    ["Shift ~$14k from Programmatic and Affiliate into Google Search and TikTok. Expected revenue lift $142000."],
    [],
    ["Top risks"],
    ["Meta creative fatigue — refresh within 7 days"],
    ["Google Search nearing saturation at $38k/wk"],
    ["Mild data drift on Meta CPMs"],
  ];
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
  return new Blob([csv], { type: "text/csv;charset=utf-8" });
}

function Report() {
  const [progress, setProgress] = useState<number | null>(null);

  function exportFile(kind: "pdf" | "csv") {
    setProgress(0);
    const id = setInterval(() => {
      setProgress((p) => {
        if (p === null) return null;
        const next = p + 12 + Math.random() * 14;
        if (next >= 100) {
          clearInterval(id);
          try {
            if (kind === "pdf") triggerDownload(buildPdf(), "aignition-report.pdf");
            else triggerDownload(buildCsv(), "aignition-report.csv");
          } catch (e) { console.error(e); }
          setTimeout(() => setProgress(null), 800);
          return 100;
        }
        return next;
      });
    }, 100);
  }


  return (
    <div>
      <PageHeader eyebrow="Step 7" title="Executive report"
        subtitle="Everything a CMO needs — in one shareable page."
        right={
          <div className="flex gap-2">
            <button onClick={() => exportFile("pdf")}
              className="inline-flex items-center gap-2 rounded-xl gradient-brand px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-lift)] hover:scale-[1.03]">
              <Download className="h-4 w-4" /> Export PDF
            </button>
            <button onClick={() => exportFile("csv")}
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-white px-4 py-2.5 text-sm font-semibold shadow-[var(--shadow-soft)] hover:shadow-[var(--shadow-lift)]">
              <FileText className="h-4 w-4" /> Export CSV
            </button>
          </div>
        }
      />

      {progress !== null && (
        <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }}
          className="mb-5 rounded-2xl border border-border bg-white p-4">
          <div className="flex items-center justify-between text-xs font-medium">
            <span>Preparing your report…</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
            <motion.div className="h-full gradient-brand" animate={{ width: `${progress}%` }} transition={{ duration: 0.2 }} />
          </div>
        </motion.div>
      )}

      <SoftCard className="border-2">
        {/* Report preview */}
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl gradient-brand text-white"><Sparkles className="h-5 w-5" /></span>
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">AIgnition · Decision Report</div>
              <div className="text-lg font-bold">Q4 marketing plan · 30-day outlook</div>
            </div>
          </div>
          <div className="text-right text-xs text-muted-foreground">
            <div>Generated today</div>
            <div>Model ensemble v3.2</div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {[
            { label: "Expected Revenue", value: `$${kpis.expectedRevenue.toLocaleString()}`, sub: `+${kpis.uplift}% vs baseline` },
            { label: "Blended ROAS", value: `${kpis.roas.toFixed(2)}x`, sub: "next 30 days" },
            { label: "Confidence", value: `${kpis.confidence}%`, sub: `MAPE ${kpis.mape}%` },
          ].map((k, i) => (
            <motion.div key={k.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="rounded-2xl border border-border bg-white p-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{k.label}</div>
              <div className="mt-2 text-2xl font-bold">{k.value}</div>
              <div className="mt-1 text-xs text-[color:var(--success)]">{k.sub}</div>
            </motion.div>
          ))}
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-border bg-white p-4">
            <div className="text-sm font-semibold">Recommendation</div>
            <p className="mt-2 text-sm text-muted-foreground">
              Apply the AI-optimized allocation: shift ~$14k from Programmatic and Affiliate into Google Search
              and TikTok. Expected revenue lift: $<AnimatedNumber value={142000} />.
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-white p-4">
            <div className="text-sm font-semibold">Top risks</div>
            <ul className="mt-2 space-y-1.5 text-sm">
              <li className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[color:var(--danger)]" /> Meta creative fatigue — refresh within 7 days</li>
              <li className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[color:var(--warning)]" /> Google Search nearing saturation at $38k/wk</li>
              <li className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[color:var(--warning)]" /> Mild data drift on Meta CPMs</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-dashed border-border p-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Executive summary</div>
          <p className="mt-2 text-sm">
            AIgnition recommends the optimized plan: <span className="font-semibold text-gradient-brand">+12.4% revenue lift</span>
            {" "}at 3.7x blended ROAS, with a single watch-level risk. Aggressive alternatives can capture more
            revenue but reintroduce fatigue and saturation risks unlikely to be resolved inside the window.
          </p>
        </div>
      </SoftCard>
    </div>
  );
}
