import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { AnimatedNumber } from "@/components/ai/AnimatedNumber";

export const Route = createFileRoute("/scenarios")({
  head: () => ({ meta: [{ title: "Scenarios — AIgnition" }, { name: "description", content: "Side-by-side comparison of current, optimized and custom scenarios." }] }),
  component: Scenarios,
});

type Sc = { key: string; name: string; tone: "muted" | "brand" | "success"; revenue: number; roas: number; risk: string; delta: number };

const scenarios: Sc[] = [
  { key: "current", name: "Current plan", tone: "muted", revenue: 1142000, roas: 3.3, risk: "2 watch flags", delta: 0 },
  { key: "optimized", name: "AI-optimized", tone: "brand", revenue: 1284000, roas: 3.7, risk: "1 watch flag", delta: 12.4 },
  { key: "aggressive", name: "Custom · aggressive", tone: "success", revenue: 1352000, roas: 3.5, risk: "2 risk flags", delta: 18.4 },
];



function Scenarios() {
  return (
    <div>
      <PageHeader eyebrow="Step 4" title="Scenario comparison"
        subtitle="Compare plans side-by-side. Green means better than current, coral means worse."
        right={
          <Link to="/copilot" className="inline-flex items-center gap-2 rounded-xl gradient-brand px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-lift)] hover:scale-[1.03]">
            Ask the copilot <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        {scenarios.map((s, i) => {
          const ring =
            s.tone === "brand" ? "ring-2 ring-[color:var(--brand)]/40" :
            s.tone === "success" ? "ring-2 ring-[color:var(--success)]/40" : "";
          return (
            <SoftCard key={s.key} delay={i * 0.1} className={ring}>
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{s.name}</div>
                {s.tone === "brand" && (
                  <span className="rounded-full gradient-brand px-2 py-0.5 text-[10px] font-semibold text-white">Recommended</span>
                )}
              </div>
              <div className="mt-3 text-3xl font-bold">
                $<AnimatedNumber value={s.revenue} />
              </div>
              <div className={`mt-1 text-xs font-semibold ${
                s.delta > 0 ? "text-[color:var(--success)]" : s.delta < 0 ? "text-[color:var(--danger)]" : "text-muted-foreground"
              }`}>
                {s.delta === 0 ? "Baseline" : `${s.delta > 0 ? "+" : ""}${s.delta}% vs current`}
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
                <div className="rounded-xl border border-border bg-white p-3">
                  <div className="text-muted-foreground">ROAS</div>
                  <div className="mt-1 text-lg font-semibold">{s.roas.toFixed(2)}x</div>
                </div>
                <div className="rounded-xl border border-border bg-white p-3">
                  <div className="text-muted-foreground">Risk profile</div>
                  <div className="mt-1 text-lg font-semibold">{s.risk}</div>
                </div>
              </div>
            </SoftCard>
          );
        })}
      </div>

      <SoftCard className="mt-6" delay={0.35}>
        <div className="text-sm font-semibold">Why AI-optimized wins</div>
        <p className="mt-2 text-sm text-muted-foreground">
          The optimized plan captures +12.4% revenue lift with only <span className="text-foreground font-medium">1 watch flag</span>,
          versus the aggressive scenario which pushes Google Search past its saturation point and reintroduces
          Meta creative-fatigue risk. Recommended unless you can refresh creative in the next 7 days.
        </p>
      </SoftCard>
    </div>
  );
}
