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
            className="relative animate-fade-in-right group"
            style={{ animationDelay: "0.2s" }}
          >
            {/* Ambient glow */}
            <div
              className="absolute -inset-6 rounded-[36px] bg-gradient-to-tr from-blue-600/15 via-transparent to-sky-400/15 blur-2xl animate-pulse"
              style={{ animationDuration: "6s" }}
            />
            {/* Scene: image (70% left) + pills panel (50% right), overlapping in the middle */}
            <div className="relative">
              {/* Full-width gradient mask — covers entire scene */}
              <div
                className="pointer-events-none absolute inset-0 z-10 rounded-[28px]"
                style={{
                  background:
                    "linear-gradient(to right, transparent 0%, rgba(15,23,42,0.15) 30%, rgba(15,23,42,0.55) 60%, rgba(15,23,42,0.85) 100%)",
                }}
              />
              {/* Image — 70% width, left-anchored */}
              <div className="relative w-[70%]">
                {/* Scale wrapper */}
                <div className="group-hover:scale-[1.02] transition-transform duration-500">
                  {/* Perspective tilt wrapper */}
                  <div
                    style={{
                      transform: "perspective(900px) rotateY(8deg) rotateX(2deg)",
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
                      <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-200 rounded-t-[28px] bg-[#f1f3f4]">
                        <div className="flex gap-[5px]">
                          <div className="size-[9px] rounded-full bg-[#ff5f57]" />
                          <div className="size-[9px] rounded-full bg-[#ffbd2e]" />
                          <div className="size-[9px] rounded-full bg-[#28c840]" />
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

              {/* Pills panel — 50% width, absolute right, full height at 85%, above mask */}
              <div className="absolute right-0 top-0 bottom-0 w-1/2 z-20 flex items-center">
                <div className="flex flex-col items-stretch w-full h-[85%]">
                  {[
                    "Brand AI Search Tracking",
                    "Brand Impression Observability",
                    "Competitive Comparison",
                    "Insight of Marketing Dynamic",
                    "Your Brand Performance Improvement Actions",
                  ].map((label, i) => (
                    <div key={label} className={i < 4 ? "flex flex-col flex-1" : "flex-shrink-0"}>
                      {/* Pill */}
                      <div
                        className={`animate-pill-pulse w-full rounded-full px-4 text-center text-xs font-bold flex items-center justify-center flex-1 ${
                          i === 4
                            ? "bg-gradient-to-r from-blue-600 to-sky-400 text-white"
                            : "bg-gradient-to-b from-blue-50 to-blue-100 text-slate-700"
                        }`}
                        style={{
                          animationDelay: `${i * 0.7}s`,
                          minHeight: "2.75rem",
                          ...(i === 4
                            ? { boxShadow: "0 4px 18px rgba(37,99,235,0.45)" }
                            : { border: "2px solid #3b82f6", boxShadow: "0 2px 8px rgba(59,130,246,0.15)" }),
                        }}
                      >
                        {label}
                      </div>
                      {/* Connector (not after last pill) */}
                      {i < 4 && (
                        <div
                          className="relative mx-auto w-[2px] flex-shrink-0"
                          style={{ height: "100%", minHeight: "1.5rem", background: "linear-gradient(180deg, rgba(59,130,246,0.3), rgba(59,130,246,0.7))" }}
                        >
                          <div
                            className="animate-dot-travel absolute left-1/2 -translate-x-1/2 size-[7px] rounded-full bg-blue-500"
                            style={{ animationDelay: `${(i + 1) * 0.7}s` }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
