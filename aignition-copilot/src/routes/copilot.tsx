import { createFileRoute } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { Send, Sparkles, User } from "lucide-react";
import { PageHeader } from "@/components/ai/PageHeader";
import { SoftCard } from "@/components/ai/Card";
import { ForecastChart } from "@/components/ai/ForecastChart";
import { generateForecast } from "@/lib/mock-data";

export const Route = createFileRoute("/copilot")({
  head: () => ({ meta: [{ title: "AI Copilot — AIgnition" }, { name: "description", content: "Chat and simulate what-ifs against your marketing forecast." }] }),
  component: Copilot,
});

type Msg = { role: "user" | "ai"; text: string };

const STARTERS = [
  "What if I increase Google budget by 20%?",
  "Where should I cut spend safely?",
  "Explain the forecast in 3 bullets for the CMO.",
];

function fakeAnswer(q: string) {
  if (/google/i.test(q))
    return "Increasing Google Search by 20% adds ~$41k revenue over 30 days, but marginal ROAS drops from 4.2x to 3.4x — you'll spend $28k for $95k. Cheaper: shift $8k from Programmatic to TikTok for similar lift with lower saturation risk.";
  if (/cut|reduce/i.test(q))
    return "Safest cuts: Programmatic (-3%) and Affiliate (-2%). Both sit below your 2.0x ROAS floor over the last 14 days with no seasonal justification. Expected revenue impact: -$4k. Expected ROAS impact: +0.3x.";
  if (/cmo|executive|summary/i.test(q))
    return "• Next 30 days: $1.28M expected revenue (+12.4% vs baseline) at 3.7x blended ROAS.\n• Reallocating from Programmatic → Google & TikTok drives the lift with 87% model confidence.\n• Watch: Meta creative fatigue could clip 2–3 points if not refreshed within 7 days.";
  return "Good question. Based on the current forecast and 5-model ensemble, the highest-EV move is to apply the AI-optimized allocation — +12.4% revenue with only one watch-level risk. Want me to draft the exec summary?";
}

function Copilot() {
  const data = useMemo(() => generateForecast(60), []);
  const [multiplier, setMultiplier] = useState(1);
  const [messages, setMessages] = useState<Msg[]>([
    { role: "ai", text: "Hi — I'm your AIgnition copilot. Ask me a what-if, or move the slider to reshape the forecast in real time." },
  ]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const shaped = useMemo(
    () => data.map((d, i) => (i < 30 ? d : { ...d, p50: d.p50 * multiplier, p10: d.p10 * multiplier, p90: d.p90 * multiplier })),
    [data, multiplier],
  );

  useEffect(() => { listRef.current?.scrollTo({ top: 9e9, behavior: "smooth" }); }, [messages, streaming]);

  function send(q: string) {
    if (!q.trim()) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    const full = fakeAnswer(q);
    setStreaming("");
    let i = 0;
    const id = setInterval(() => {
      i += Math.max(1, Math.round(full.length / 60));
      const slice = full.slice(0, i);
      if (i >= full.length) {
        clearInterval(id);
        setStreaming(null);
        setMessages((m) => [...m, { role: "ai", text: full }]);
      } else {
        setStreaming(slice);
      }
    }, 28);
  }

  return (
    <div>
      <PageHeader eyebrow="Step 5" title="AI copilot · what-if simulator"
        subtitle="Ask questions in plain English or drag the slider to reshape the forecast live." />

      <div className="grid gap-6 lg:grid-cols-5">
        <SoftCard className="lg:col-span-3">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold">Interactive forecast</div>
              <div className="text-xs text-muted-foreground">Multiplier {multiplier.toFixed(2)}x applied to forward projection</div>
            </div>
            <div className="text-xs text-muted-foreground">P10 · P50 · P90</div>
          </div>
          <ForecastChart data={shaped} />
          <div className="mt-4">
            <label className="text-xs font-medium text-muted-foreground">Budget multiplier</label>
            <input
              type="range" min={0.6} max={1.4} step={0.02} value={multiplier}
              onChange={(e) => setMultiplier(parseFloat(e.target.value))}
              className="mt-2 w-full accent-[color:var(--brand)]"
            />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>0.6x</span><span>1.0x baseline</span><span>1.4x</span>
            </div>
          </div>
        </SoftCard>

        <SoftCard className="lg:col-span-2 flex flex-col">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <span className="grid h-6 w-6 place-items-center rounded-lg gradient-brand text-white"><Sparkles className="h-3.5 w-3.5" /></span>
            Copilot
          </div>

          <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto pr-1" style={{ maxHeight: 380 }}>
            <AnimatePresence initial={false}>
              {messages.map((m, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-2 ${m.role === "user" ? "justify-end" : ""}`}>
                  {m.role === "ai" && <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg gradient-brand text-white"><Sparkles className="h-3 w-3" /></span>}
                  <div className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-sm ${
                    m.role === "user" ? "gradient-brand text-white" : "bg-muted text-foreground"
                  }`}>{m.text}</div>
                  {m.role === "user" && <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-foreground text-white"><User className="h-3 w-3" /></span>}
                </motion.div>
              ))}
              {streaming !== null && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2">
                  <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-lg gradient-brand text-white"><Sparkles className="h-3 w-3" /></span>
                  <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl bg-muted px-3 py-2 text-sm">
                    {streaming}<span className="ml-0.5 inline-block h-3 w-1.5 translate-y-0.5 animate-pulse bg-[color:var(--brand)]" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="mt-3 flex flex-wrap gap-1.5">
            {STARTERS.map((s) => (
              <button key={s} onClick={() => send(s)}
                className="rounded-full border border-border bg-white px-2.5 py-1 text-[11px] font-medium text-muted-foreground transition hover:text-foreground hover:shadow-[var(--shadow-soft)]">
                {s}
              </button>
            ))}
          </div>

          <form onSubmit={(e) => { e.preventDefault(); send(input); }} className="mt-3 flex items-center gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a what-if…"
              className="flex-1 rounded-xl border border-border bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[color:var(--brand)]/30" />
            <button type="submit" className="grid h-9 w-9 place-items-center rounded-xl gradient-brand text-white shadow-[var(--shadow-lift)] hover:scale-[1.05]">
              <Send className="h-4 w-4" />
            </button>
          </form>
        </SoftCard>
      </div>

      <SoftCard className="mt-6" delay={0.2}>
        <div className="text-sm font-semibold">Executive summary <span className="text-xs font-normal text-muted-foreground">· auto-generated</span></div>
        <TypingSummary text={
          "Over the next 30 days, AIgnition projects $1.28M in revenue at 3.7x blended ROAS — a +12.4% lift versus current pacing, with 87% model confidence. The largest driver is a reallocation of ~$14k from Programmatic and Affiliate into Google Search and TikTok, where marginal ROAS remains well above the 2.0x floor. Meta creative fatigue is the main downside risk; a refresh within 7 days would protect roughly 2–3 points of the projected lift."
        } />
      </SoftCard>
    </div>
  );
}

function TypingSummary({ text }: { text: string }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    if (n >= text.length) return;
    const t = setTimeout(() => setN((v) => Math.min(text.length, v + 4)), 20);
    return () => clearTimeout(t);
  }, [n, text]);
  return (
    <p className="mt-2 text-sm text-muted-foreground">
      {text.slice(0, n)}
      {n < text.length && <span className="ml-0.5 inline-block h-3 w-1.5 translate-y-0.5 animate-pulse bg-[color:var(--brand)]" />}
    </p>
  );
}
