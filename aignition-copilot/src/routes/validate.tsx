import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Check, ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { ConfidenceGauge } from "@/components/ai/ConfidenceGauge";
import { validationSteps } from "@/lib/mock-data";

export const Route = createFileRoute("/validate")({
  head: () => ({ meta: [{ title: "Validate — AIgnition" }, { name: "description", content: "Automated data-quality checks before forecasting." }] }),
  component: Validate,
});

function Validate() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (step >= validationSteps.length) return;
    const t = setTimeout(() => setStep((s) => s + 1), 420);
    return () => clearTimeout(t);
  }, [step]);

  const done = step >= validationSteps.length;

  return (
    <div>
      <PageHeader eyebrow="Step 1" title="Data validation"
        subtitle="We check your CSV for the issues that quietly ruin forecasts."
        right={
          done ? (
            <Link to="/forecast" className="inline-flex items-center gap-2 rounded-xl gradient-brand px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-lift)] hover:scale-[1.03]">
              Continue to forecast <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <SoftCard className="lg:col-span-2">
          <div className="mb-2 text-sm font-semibold">Checks</div>
          <ul className="divide-y divide-border">
            {validationSteps.map((s, i) => {
              const active = i < step;
              return (
                <li key={s.label} className="flex items-center justify-between py-3">
                  <div className="flex items-center gap-3">
                    <motion.div
                      initial={false}
                      animate={{
                        backgroundColor: active ? "var(--success)" : "var(--muted)",
                        color: active ? "white" : "var(--muted-foreground)",
                        scale: active ? 1 : 0.9,
                      }}
                      className="grid h-7 w-7 place-items-center rounded-full"
                    >
                      {active ? <Check className="h-4 w-4" /> : <span className="text-xs">{i + 1}</span>}
                    </motion.div>
                    <div>
                      <div className="text-sm font-medium">{s.label}</div>
                      <div className="text-xs text-muted-foreground">{s.detail}</div>
                    </div>
                  </div>
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: active ? 1 : 0.3 }}
                    className="text-xs font-semibold text-[color:var(--success)]">
                    {active ? "Passed" : "…"}
                  </motion.div>
                </li>
              );
            })}
          </ul>
        </SoftCard>

        <SoftCard delay={0.1}>
          <div className="mb-4 text-sm font-semibold">Data Quality Score</div>
          <div className="flex flex-col items-center gap-3">
            <ConfidenceGauge value={done ? 92 : Math.round((step / validationSteps.length) * 92)} size={160} />
            <div className="text-center text-xs text-muted-foreground">
              {done ? "Your dataset is ready for probabilistic forecasting." : "Running validation…"}
            </div>
          </div>
        </SoftCard>
      </div>
    </div>
  );
}
