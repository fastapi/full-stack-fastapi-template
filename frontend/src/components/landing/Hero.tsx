// src/components/landing/Hero.tsx
import { SignUpButton } from "@clerk/clerk-react"
import { Button } from "@/components/ui/button.tsx"

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 via-white to-slate-50 py-24">
      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute -top-24 right-[-10%] h-[420px] w-[420px] rounded-full bg-blue-500/20 blur-3xl animate-pulse"
          style={{ animationDuration: "4s" }}
        />
        <div
          className="absolute top-32 left-[-15%] h-[360px] w-[360px] rounded-full bg-sky-400/20 blur-3xl animate-pulse"
          style={{ animationDuration: "5s", animationDelay: "1s" }}
        />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(15,23,42,0.08),transparent_45%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(15,23,42,0.05),transparent_40%,rgba(59,130,246,0.06))]" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr,0.9fr] gap-12 items-center">
          <div className="animate-fade-in-up">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold text-slate-600 shadow-sm hover:shadow-md transition-shadow">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
              </span>
              AI Search Intelligence
              <span className="text-slate-400">•</span>
              Market Leaders
            </div>
            <h1 className="font-display font-bold text-4xl sm:text-5xl md:text-6xl tracking-tight leading-[1.05] text-slate-900 mt-5">
              Turn AI Search Into{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-sky-500">
                Growth Intelligence
              </span>
            </h1>
            <p className="font-body text-base sm:text-lg text-slate-600 leading-relaxed mt-6 max-w-2xl">
              AI search is now the first impression for buyers. Kila makes your
              AI visibility measurable, competitive, and actionable.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <SignUpButton mode="modal" forceRedirectUrl="/app/brands">
                <Button
                  size={"lg"}
                  className="bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all"
                >
                  Start Free Trial
                </Button>
              </SignUpButton>
              <Button
                variant={"outline"}
                size="lg"
                className="hover:bg-slate-50 transition-colors"
              >
                Watch Demo
              </Button>
            </div>
            <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-slate-600">
              {[
                { label: "Daily AI visibility tracking" },
                { label: "Competitor gap alerts" },
                { label: "Segment‑level insight signals" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-xl border border-slate-200 bg-white/80 px-4 py-3 shadow-sm hover:shadow-md transition-shadow cursor-default"
                >
                  <span className="font-semibold text-slate-900">
                    {item.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div
            className="relative animate-fade-in-right"
            style={{ animationDelay: "0.2s" }}
          >
            <div
              className="absolute -inset-6 rounded-[36px] bg-gradient-to-tr from-blue-600/15 via-transparent to-sky-400/15 blur-2xl animate-pulse"
              style={{ animationDuration: "6s" }}
            />
            <div className="relative rounded-[28px] border border-slate-200/70 bg-white shadow-[0_30px_80px_-50px_rgba(15,23,42,0.6)] overflow-hidden group">
              <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-r from-slate-900/5 to-transparent" />
              <img
                src="/assets/screens/brand-impression.png"
                alt="Kila brand impression dashboard"
                className="w-full h-full object-cover transform group-hover:scale-[1.02] transition-transform duration-500"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
