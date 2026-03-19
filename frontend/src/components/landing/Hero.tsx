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
            className="relative animate-fade-in-right pr-8 group"
            style={{ animationDelay: "0.2s" }}
          >
            {/* Ambient glow — unchanged */}
            <div
              className="absolute -inset-6 rounded-[36px] bg-gradient-to-tr from-blue-600/15 via-transparent to-sky-400/15 blur-2xl animate-pulse"
              style={{ animationDuration: "6s" }}
            />
            {/* Scale wrapper — Tailwind hover scale must be on a separate div from the
                inline transform, otherwise the inline style wins and scale is silently ignored */}
            <div className="relative group-hover:scale-[1.02] transition-transform duration-500">
              {/* Perspective tilt wrapper */}
              <div
                style={{
                  transform: "perspective(700px) rotateY(14deg) rotateX(3deg)",
                  transformOrigin: "left center",
                }}
              >
                <div
                  className="rounded-[28px] bg-white border border-blue-500/[0.14]"
                  style={{
                    boxShadow:
                      "24px 32px 70px -10px rgba(15,23,42,0.35), -4px 4px 20px -4px rgba(59,130,246,0.2)",
                  }}
                >
                  {/* Browser chrome bar */}
                  <div
                    className="flex items-center gap-2 px-3 py-2 border-b border-slate-200 rounded-t-[28px]"
                    style={{ background: "#f1f3f4" }}
                  >
                    <div className="flex gap-[5px]">
                      <div className="size-[9px] rounded-full" style={{ background: "#ff5f57" }} />
                      <div className="size-[9px] rounded-full" style={{ background: "#ffbd2e" }} />
                      <div className="size-[9px] rounded-full" style={{ background: "#28c840" }} />
                    </div>
                    <div className="flex-1 bg-white rounded border border-slate-200 px-2 py-[3px] text-[9px] text-slate-400">
                      app.kila.ai
                    </div>
                  </div>
                  {/* Screenshot */}
                  <img
                    src="/assets/screens/brand-impression.png"
                    alt="Kila brand impression dashboard"
                    className="w-full object-cover"
                    style={{ display: "block", borderRadius: "0 0 28px 28px" }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
