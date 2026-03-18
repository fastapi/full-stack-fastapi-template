import { AlertTriangle, Eye, Swords, TrendingUp } from "lucide-react"

export default function ProductSection() {
  return (
    <section className="relative py-24 bg-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-[-10%] h-[420px] w-[420px] rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute top-[35%] right-[-15%] h-[460px] w-[460px] rounded-full bg-sky-400/10 blur-3xl" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Row 1 — Problem statement */}
        <div className="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-10 sm:px-10">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
            The Problem
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900 mt-4">
            AI answers are quietly redirecting your customers to competitors —
            you won't even know you're losing without AI visibility.
          </h2>
          <p className="font-body text-sm text-slate-600 mt-4 max-w-3xl">
            Traditional SEO doesn't reveal how AI systems rank, cite, and
            describe your brand. Kila makes AI search performance measurable.
          </p>
        </div>

        {/* Row 2 — Brand Impression */}
        <div className="group mt-20 overflow-hidden rounded-[32px] border border-slate-200/70 bg-white shadow-[0_28px_70px_-40px_rgba(15,23,42,0.45)] hover:shadow-[0_35px_80px_-40px_rgba(15,23,42,0.55)] transition-all duration-500 hover:border-slate-300/70">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="p-10 sm:p-12 lg:p-14">
              <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 text-blue-700 px-3 py-1 text-xs font-semibold group-hover:bg-blue-100 transition-colors">
                <Eye className="h-4 w-4" />
                Brand Impression
              </div>
              <h3 className="font-display font-semibold text-3xl sm:text-4xl tracking-tight text-slate-900 mt-5 group-hover:text-blue-900 transition-colors">
                AI visibility, ranking, and citations — in one place.
              </h3>
              <p className="font-body text-base text-slate-600 mt-4 max-w-xl">
                Track how AI systems surface your brand, which sources they
                cite, and how your presence shifts over time.
              </p>
              <div className="mt-8 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-blue-300 group-hover:bg-blue-50 transition-colors">
                  Visibility Share
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-blue-300 group-hover:bg-blue-50 transition-colors">
                  Ranking Strength
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-blue-300 group-hover:bg-blue-50 transition-colors">
                  AI References
                </span>
              </div>
            </div>
            <div className="relative min-h-[300px] sm:min-h-[340px] lg:min-h-[380px] overflow-hidden">
              <div
                className="absolute inset-0 bg-cover bg-left group-hover:scale-105 transition-transform duration-700"
                style={{
                  backgroundImage:
                    "url('/assets/screens/brand-impression.png')",
                  WebkitMaskImage:
                    "linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.2) 20%, rgba(0,0,0,0.85) 55%, #000 100%)",
                  maskImage:
                    "linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.2) 20%, rgba(0,0,0,0.85) 55%, #000 100%)",
                }}
              />
            </div>
          </div>
        </div>

        {/* Row 3 — Competitive Analysis */}
        <div className="group mt-20 overflow-hidden rounded-[32px] border border-slate-200/70 bg-white shadow-[0_28px_70px_-40px_rgba(15,23,42,0.45)] hover:shadow-[0_35px_80px_-40px_rgba(15,23,42,0.55)] transition-all duration-500 hover:border-slate-300/70">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="relative min-h-[300px] sm:min-h-[340px] lg:min-h-[380px] order-2 lg:order-1 overflow-hidden">
              <div
                className="absolute inset-0 bg-cover bg-right group-hover:scale-105 transition-transform duration-700"
                style={{
                  backgroundImage:
                    "url('/assets/screens/competitive-analysis.png')",
                  WebkitMaskImage:
                    "linear-gradient(90deg, #000 0%, rgba(0,0,0,0.85) 45%, rgba(0,0,0,0.2) 80%, transparent 100%)",
                  maskImage:
                    "linear-gradient(90deg, #000 0%, rgba(0,0,0,0.85) 45%, rgba(0,0,0,0.2) 80%, transparent 100%)",
                }}
              />
            </div>
            <div className="p-10 sm:p-12 lg:p-14 order-1 lg:order-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 text-indigo-700 px-3 py-1 text-xs font-semibold group-hover:bg-indigo-100 transition-colors">
                <Swords className="h-4 w-4" />
                Competitive Analysis
              </div>
              <h3 className="font-display font-semibold text-3xl sm:text-4xl tracking-tight text-slate-900 mt-5 group-hover:text-indigo-900 transition-colors">
                See who's winning the AI shelf — and why.
              </h3>
              <p className="font-body text-base text-slate-600 mt-4 max-w-xl">
                Compare visibility and ranking against competitors, spot
                displacement early, and defend your position before it erodes.
              </p>
              <div className="mt-8 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-indigo-300 group-hover:bg-indigo-50 transition-colors">
                  Gap Tracking
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-indigo-300 group-hover:bg-indigo-50 transition-colors">
                  Competitor Breakthroughs
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-indigo-300 group-hover:bg-indigo-50 transition-colors">
                  Rank Displacement
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Row 4 — Market Dynamic */}
        <div className="group mt-20 overflow-hidden rounded-[32px] border border-slate-200/70 bg-white shadow-[0_28px_70px_-40px_rgba(15,23,42,0.45)] hover:shadow-[0_35px_80px_-40px_rgba(15,23,42,0.55)] transition-all duration-500 hover:border-slate-300/70">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="p-10 sm:p-12 lg:p-14">
              <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 text-slate-700 px-3 py-1 text-xs font-semibold group-hover:bg-slate-200 transition-colors">
                <TrendingUp className="h-4 w-4" />
                Market Dynamic
              </div>
              <h3 className="font-display font-semibold text-3xl sm:text-4xl tracking-tight text-slate-900 mt-5 group-hover:text-slate-800 transition-colors">
                Track market momentum before it hits revenue.
              </h3>
              <p className="font-body text-base text-slate-600 mt-4 max-w-xl">
                See category shifts, visibility volatility, and emerging
                patterns driven by AI search behavior.
              </p>
              <div className="mt-8 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-slate-400 group-hover:bg-slate-50 transition-colors">
                  Momentum
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-slate-400 group-hover:bg-slate-50 transition-colors">
                  Volatility
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-slate-400 group-hover:bg-slate-50 transition-colors">
                  Share Shifts
                </span>
              </div>
            </div>
            <div className="relative min-h-[300px] sm:min-h-[340px] lg:min-h-[380px] overflow-hidden">
              <div
                className="absolute inset-0 bg-cover bg-left group-hover:scale-105 transition-transform duration-700"
                style={{
                  backgroundImage: "url('/assets/screens/market-dynamic.png')",
                  WebkitMaskImage:
                    "linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.2) 20%, rgba(0,0,0,0.85) 55%, #000 100%)",
                  maskImage:
                    "linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.2) 20%, rgba(0,0,0,0.85) 55%, #000 100%)",
                }}
              />
            </div>
          </div>
        </div>

        {/* Row 5 — Risk Intelligence */}
        <div className="group mt-20 overflow-hidden rounded-[32px] border border-slate-200/70 bg-white shadow-[0_28px_70px_-40px_rgba(15,23,42,0.45)] hover:shadow-[0_35px_80px_-40px_rgba(15,23,42,0.55)] transition-all duration-500 hover:border-slate-300/70">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="relative min-h-[300px] sm:min-h-[340px] lg:min-h-[380px] order-2 lg:order-1 overflow-hidden">
              <div
                className="absolute inset-0 bg-cover bg-right group-hover:scale-105 transition-transform duration-700"
                style={{
                  backgroundImage:
                    "url('/assets/screens/risk-intelligence.png')",
                  WebkitMaskImage:
                    "linear-gradient(90deg, #000 0%, rgba(0,0,0,0.85) 45%, rgba(0,0,0,0.2) 80%, transparent 100%)",
                  maskImage:
                    "linear-gradient(90deg, #000 0%, rgba(0,0,0,0.85) 45%, rgba(0,0,0,0.2) 80%, transparent 100%)",
                }}
              />
            </div>
            <div className="p-10 sm:p-12 lg:p-14 order-1 lg:order-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-rose-50 text-rose-700 px-3 py-1 text-xs font-semibold group-hover:bg-rose-100 transition-colors">
                <AlertTriangle className="h-4 w-4" />
                Risk Intelligence
              </div>
              <h3 className="font-display font-semibold text-3xl sm:text-4xl tracking-tight text-slate-900 mt-5 group-hover:text-rose-900 transition-colors">
                Early‑warning signals before your visibility drops.
              </h3>
              <p className="font-body text-base text-slate-600 mt-4 max-w-xl">
                Detect erosion, rank displacement, and new entrants so you can
                act before the market shifts against you.
              </p>
              <div className="mt-8 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-rose-300 group-hover:bg-rose-50 transition-colors">
                  Erosion Alerts
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-rose-300 group-hover:bg-rose-50 transition-colors">
                  New Entrants
                </span>
                <span className="rounded-full border border-slate-200 bg-white px-3 py-1 group-hover:border-rose-300 group-hover:bg-rose-50 transition-colors">
                  Volatility Spikes
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
