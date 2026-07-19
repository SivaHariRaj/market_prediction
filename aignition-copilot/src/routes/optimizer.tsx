import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useState } from "react";
import { ArrowRight, Sparkles, CheckCircle2 } from "lucide-react";
import { Bar, BarChart, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { AnimatedNumber } from "@/components/ai/AnimatedNumber";
import { channels } from "@/lib/mock-data";

export const Route = createFileRoute("/optimizer")({
  head: () => ({ meta: [{ title: "Budget Optimizer — AIgnition" }, { name: "description", content: "Optimize channel allocation under your constraints." }] }),
  component: Optimizer,
});

function Optimizer() {
  const [applied, setApplied] = useState(false);
  const data = channels.map((c) => ({ ...c, value: applied ? c.optimized : c.current }));
  const totalUplift = 12.4;

  return (
    <div>
      <PageHeader eyebrow="Step 3" title="Budget optimizer"
        subtitle="Reallocate spend across channels to maximize expected revenue under your constraints."
        right={
          <Link to="/scenarios" className="inline-flex items-center gap-2 rounded-xl gradient-brand px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-lift)] hover:scale-[1.03]">
            Compare scenarios <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <SoftCard className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold">Channel allocation</div>
              <div className="text-xs text-muted-foreground">{applied ? "Optimized mix" : "Current mix"} · % of total budget</div>
            </div>
            <motion.button
              onClick={() => setApplied((v) => !v)}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center gap-2 rounded-xl gradient-brand px-4 py-2 text-sm font-semibold text-white shadow-[var(--shadow-lift)]"
            >
              {applied ? <CheckCircle2 className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
              {applied ? "Optimization applied" : "Apply optimization"}
            </motion.button>
          </div>

          <div className="h-[340px]">
            <ResponsiveContainer>
              <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" hide domain={[0, 45]} />
                <YAxis type="category" dataKey="name" width={120} tickLine={false} axisLine={false}
                  tick={{ fill: "var(--foreground)", fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: "1px solid var(--border)", fontSize: 12 }}
                  formatter={(v: number) => `${v}%`}
                />
                <Bar dataKey="value" radius={[8, 8, 8, 8]} isAnimationActive animationDuration={900}>
                  {data.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SoftCard>

        <div className="flex flex-col gap-4">
          <SoftCard delay={0.1}>
            <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Expected uplift</div>
            <div className="mt-2 text-4xl font-bold text-gradient-brand">
              +<AnimatedNumber value={applied ? totalUplift : 0} format={(n) => n.toFixed(1)} />%
            </div>
            <div className="mt-1 text-xs text-muted-foreground">vs current allocation, next 30 days</div>
          </SoftCard>

          <SoftCard delay={0.18}>
            <div className="text-sm font-semibold">Optimization strategy</div>
            <ul className="mt-3 space-y-2 text-xs text-muted-foreground">
              <li className="flex justify-between"><span>Total budget cap</span><span className="font-medium text-foreground">$420,000 / mo</span></li>
              <li className="flex justify-between"><span>Min per channel</span><span className="font-medium text-foreground">3%</span></li>
              <li className="flex justify-between"><span>Max per channel</span><span className="font-medium text-foreground">40%</span></li>
              <li className="flex justify-between"><span>ROAS floor</span><span className="font-medium text-foreground">2.0x</span></li>
              <li className="flex justify-between"><span>Solver</span><span className="font-medium text-foreground">Bayesian marginal ROAS</span></li>
            </ul>
          </SoftCard>
        </div>
      </div>

      <SoftCard className="mt-6" delay={0.25}>
        <div className="mb-3 text-sm font-semibold">Per-channel change</div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {channels.map((c) => {
            const delta = c.optimized - c.current;
            const positive = delta >= 0;
            return (
              <div key={c.name} className="flex items-center justify-between rounded-xl border border-border bg-white p-3">
                <div>
                  <div className="text-sm font-medium">{c.name}</div>
                  <div className="text-xs text-muted-foreground">ROAS {c.roas.toFixed(1)}x</div>
                </div>
                <div className={`text-sm font-semibold ${positive ? "text-[color:var(--success)]" : "text-[color:var(--danger)]"}`}>
                  {positive ? "+" : ""}{delta}%
                </div>
              </div>
            );
          })}
        </div>
      </SoftCard>
    </div>
  );
}
