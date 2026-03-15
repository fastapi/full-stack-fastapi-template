import { useEffect, useState } from "react"

export default function TestimonialSection() {
  const [current, setCurrent] = useState(0)

  const testimonials = [
    {
      quote: "This platform transformed our workflows. Game-changing!",
      author: "Sarah Chen",
      role: "CEO, TechCorp",
    },
    {
      quote: "Best investment we made. ROI in the first month.",
      author: "Michael Ross",
      role: "CTO, InnovateLabs",
    },
    {
      quote: "Exceptional support. They care about our success.",
      author: "Emily Stone",
      role: "VP Operations, DataFlow",
    },
  ]

  const logos = [
    "TechCorp",
    "InnovateLabs",
    "DataFlow",
    "CloudSync",
    "StartupHub",
    "ScaleUp",
  ]

  useEffect(() => {
    const interval = setInterval(
      () => setCurrent((prev) => (prev + 1) % testimonials.length),
      5000,
    )
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="relative py-24 bg-slate-950">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 right-[-10%] h-[380px] w-[380px] rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute bottom-[-20%] left-[-10%] h-[420px] w-[420px] rounded-full bg-sky-400/20 blur-3xl" />
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-white mb-12 text-center">
          What Our Customers Say
        </h2>

        <div className="bg-slate-900/70 p-8 rounded-2xl shadow-[0_28px_80px_-60px_rgba(15,23,42,0.9)] border border-slate-800/80 mb-12 min-h-[200px]">
          <div className="text-3xl text-blue-400 mb-4">"</div>
          <p className="font-body text-base leading-relaxed text-slate-200 mb-6 italic">
            {testimonials[current].quote}
          </p>
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-sky-500 rounded-full flex items-center justify-center text-white font-bold mr-4">
              {testimonials[current].author.charAt(0)}
            </div>
            <div>
              <div className="font-display font-semibold text-base tracking-tight text-white">
                {testimonials[current].author}
              </div>
              <div className="font-body text-xs tracking-[0.2em] uppercase text-slate-400">
                {testimonials[current].role}
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-body font-medium text-xs tracking-[0.2em] uppercase text-center text-slate-400 mb-6">
            Trusted by leading companies
          </h3>
          <div className="flex flex-wrap justify-center gap-8">
            {logos.map((logo, idx) => (
              <div
                key={idx}
                className="bg-white/5 px-6 py-4 rounded-xl border border-white/10"
              >
                <span className="font-display font-medium text-sm tracking-[0.04em] text-slate-200">
                  {logo}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
