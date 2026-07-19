import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect } from "react";

export function ConfidenceGauge({ value, size = 128 }: { value: number; size?: number }) {
  const r = size / 2 - 10;
  const c = 2 * Math.PI * r;
  const mv = useMotionValue(0);
  const dash = useTransform(mv, (v) => `${(v / 100) * c} ${c}`);
  const label = useTransform(mv, (v) => Math.round(v).toString());
  useEffect(() => {
    const ctrl = animate(mv, value, { duration: 1.6, ease: [0.22, 1, 0.36, 1] });
    return ctrl.stop;
  }, [value, mv]);
  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id="gauge" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="var(--brand)" />
            <stop offset="100%" stopColor="var(--brand-2)" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} stroke="var(--border)" strokeWidth={10} fill="none" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r}
          stroke="url(#gauge)" strokeWidth={10} strokeLinecap="round" fill="none"
          style={{ strokeDasharray: dash }}
        />
      </svg>
      <div className="absolute text-center">
        <motion.div className="text-2xl font-bold">{label}</motion.div>
        <div className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">Confidence</div>
      </div>
    </div>
  );
}
