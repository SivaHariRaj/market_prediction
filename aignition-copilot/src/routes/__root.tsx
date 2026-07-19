import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  useRouterState,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, type ReactNode } from "react";
import { Sparkles, Home, ChevronLeft, ChevronRight, Check } from "lucide-react";

const STEPS = [
  { path: "/validate", label: "Validate" },
  { path: "/forecast", label: "Forecast" },
  { path: "/optimizer", label: "Optimize" },
  { path: "/scenarios", label: "Scenarios" },
  { path: "/risks", label: "Risks" },
  { path: "/copilot", label: "Copilot" },
  { path: "/report", label: "Report" },
] as const;

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-gradient-brand">404</h1>
        <h2 className="mt-4 text-xl font-semibold">Page not found</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The page you're looking for doesn't exist.
        </p>
        <Link to="/" className="mt-6 inline-flex rounded-lg gradient-brand px-4 py-2 text-sm font-medium text-white">
          Go home
        </Link>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => { reportLovableError(error, { boundary: "root" }); }, [error]);
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="mt-2 text-sm text-muted-foreground">Try refreshing the page.</p>
        <button
          onClick={() => { router.invalidate(); reset(); }}
          className="mt-6 rounded-lg gradient-brand px-4 py-2 text-sm font-medium text-white"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "AIgnition — AI Marketing Decision Copilot" },
      { name: "description", content: "Forecast, optimize budgets, simulate scenarios and detect risks — AIgnition is the AI copilot for marketing decisions." },
      { property: "og:title", content: "AIgnition — AI Marketing Decision Copilot" },
      { property: "og:description", content: "Forecast, optimize budgets, simulate scenarios and detect risks with an AI-powered marketing copilot." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head><HeadContent /></head>
      <body>{children}<Scripts /></body>
    </html>
  );
}

function TopNav() {
  return (
    <header className="sticky top-0 z-40">
      <div className="glass mx-auto mt-3 flex max-w-7xl items-center justify-between rounded-2xl px-4 py-2.5 md:px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-xl gradient-brand text-white shadow-[var(--shadow-lift)]">
            <Sparkles className="h-4 w-4" />
          </span>
          <span className="text-base font-bold tracking-tight">AIgnition</span>
        </Link>
        <Link to="/report" className="rounded-lg gradient-brand px-3.5 py-1.5 text-xs font-semibold text-white shadow-[var(--shadow-lift)] transition hover:scale-[1.03]">
          Export Report
        </Link>
      </div>
    </header>
  );
}


function AnimatedOutlet() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={path}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      >
        <Outlet />
      </motion.div>
    </AnimatePresence>
  );
}

function StepNav() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  if (path === "/") return null;
  const idx = STEPS.findIndex((s) => s.path === path);
  if (idx === -1) return null;
  const prev = idx > 0 ? STEPS[idx - 1] : null;
  const next = idx < STEPS.length - 1 ? STEPS[idx + 1] : null;

  return (
    <div className="mx-auto mt-4 max-w-7xl px-4 md:px-6">
      <div className="glass flex flex-col gap-3 rounded-2xl p-3 md:p-4">
        <div className="flex items-center gap-2">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 rounded-lg border border-border/60 bg-white/60 px-2.5 py-1.5 text-xs font-medium text-foreground/80 transition hover:bg-white"
          >
            <Home className="h-3.5 w-3.5" /> Home
          </Link>
          <div className="ml-auto flex items-center gap-2">
            {prev ? (
              <Link
                to={prev.path}
                className="inline-flex items-center gap-1 rounded-lg border border-border/60 bg-white/60 px-2.5 py-1.5 text-xs font-medium transition hover:bg-white"
              >
                <ChevronLeft className="h-3.5 w-3.5" /> {prev.label}
              </Link>
            ) : null}
            {next ? (
              <Link
                to={next.path}
                className="inline-flex items-center gap-1 rounded-lg gradient-brand px-3 py-1.5 text-xs font-semibold text-white shadow-[var(--shadow-lift)]"
              >
                {next.label} <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            ) : null}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          {STEPS.map((s, i) => {
            const active = i === idx;
            const done = i < idx;
            return (
              <Link
                key={s.path}
                to={s.path}
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium transition ${
                  active
                    ? "gradient-brand text-white shadow-[var(--shadow-lift)]"
                    : done
                    ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                    : "border border-border/60 bg-white/60 text-muted-foreground hover:bg-white"
                }`}
              >
                <span className={`grid h-4 w-4 place-items-center rounded-full text-[10px] ${
                  active ? "bg-white/25" : done ? "bg-emerald-600 text-white" : "bg-muted"
                }`}>
                  {done ? <Check className="h-2.5 w-2.5" /> : i + 1}
                </span>
                {s.label}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <TopNav />
      <StepNav />
      <main className="mx-auto max-w-7xl px-4 py-6 md:px-6 md:py-10">
        <AnimatedOutlet />
      </main>
      <footer className="mx-auto max-w-7xl px-4 pb-10 pt-4 text-xs text-muted-foreground md:px-6">
        AIgnition · AI Marketing Decision Copilot · Demo build
      </footer>
    </QueryClientProvider>
  );
}
