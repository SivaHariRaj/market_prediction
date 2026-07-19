import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { AlertTriangle, ShieldCheck, Eye } from "lucide-react";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { risks } from "@/lib/mock-data";

export const Route = createFileRoute("/risks")({
  head: () => ({ meta: [{ title: "Risk Detection — AIgnition" }, { name: "description", content: "Detects saturation, creative fatigue, drift and other silent failures." }] }),
  component: Risks,
});

const tone = {
  healthy: { color: "var(--success)", label: "Healthy", Icon: ShieldCheck, pulse: false },
  watch: { color: "var(--warning)", label: "Watch", Icon: Eye, pulse: true },
  risk: { color: "var(--danger)", label: "Risk", Icon: AlertTriangle, pulse: true },
} as const;

function Risks() {
  return (
    <div>
      <PageHeader eyebrow="Step 6" title="Risk detection"
        subtitle="Silent failures AIgnition watches so your forecast doesn't lie to you." />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {risks.map((r, i) => {
          const t = tone[r.severity];
          return (
            <SoftCard key={r.id} delay={i * 0.06}>
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.color }}>{t.label}</div>
                <motion.span
                  initial={{ scale: 0.6, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2 + i * 0.05, type: "spring", stiffness: 240 }}
                  className={`grid h-8 w-8 place-items-center rounded-full ${t.pulse ? "pulse-soft" : ""}`}
                  style={{ backgroundColor: `color-mix(in oklab, ${t.color} 15%, white)`, color: t.color }}
                >
                  <t.Icon className="h-4 w-4" />
                </motion.span>
              </div>
              <div className="mt-3 text-base font-semibold">{r.title}</div>
              <div className="mt-1 text-xs text-muted-foreground">{r.description}</div>
              <div className="mt-4 flex items-center justify-between rounded-xl bg-muted/70 px-3 py-2 text-xs">
                <span className="text-muted-foreground">Signal</span>
                <span className="font-semibold" style={{ color: t.color }}>{r.metric}</span>
              </div>
            </SoftCard>
          );
        })}
      </div>
    </div>
  );
}
