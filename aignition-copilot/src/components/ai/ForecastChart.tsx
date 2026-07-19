import { Area, AreaChart, CartesianGrid, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ForecastPoint } from "@/lib/mock-data";
import { motion } from "framer-motion";

export function ForecastChart({ data, showActual = false }: { data: ForecastPoint[]; showActual?: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="h-[340px] w-full"
    >
      <ResponsiveContainer>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--brand-2)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--brand)" stopOpacity={0.06} />
            </linearGradient>
            <linearGradient id="p50line" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="var(--brand)" />
              <stop offset="100%" stopColor="var(--brand-2)" />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 6" vertical={false} />
          <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fill: "var(--muted-foreground)", fontSize: 11 }} />
          <YAxis tickLine={false} axisLine={false} tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
            tickFormatter={(v) => `$${Math.round(v / 1000)}k`} width={48} />
          <Tooltip
            contentStyle={{ borderRadius: 12, border: "1px solid var(--border)", boxShadow: "var(--shadow-soft)", fontSize: 12 }}
            formatter={(v: number) => `$${Math.round(v).toLocaleString()}`}
          />
          <Area type="monotone" dataKey="p90" stroke="none" fill="url(#band)" isAnimationActive
            animationDuration={1400} animationEasing="ease-out" />
          <Area type="monotone" dataKey="p10" stroke="none" fill="var(--background)" isAnimationActive
            animationDuration={1400} animationEasing="ease-out" />
          <Line type="monotone" dataKey="p50" stroke="url(#p50line)" strokeWidth={3} dot={false}
            isAnimationActive animationDuration={1600} animationEasing="ease-out" />
          {showActual && (
            <Line type="monotone" dataKey="actual" stroke="var(--success)" strokeWidth={2}
              strokeDasharray="4 4" dot={false} isAnimationActive animationDuration={1600} />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
