import { Play, Star } from "lucide-react"
import { useEffect, useState } from "react"

interface Testimonial {
  quote: string
  author: string
  role: string
  company: string
  rating: number
  avatar?: string
}

const testimonials: Testimonial[] = [
  {
    quote:
      "Kila transformed how we track our AI visibility. We discovered our competitors were mentioned 3x more in AI results and were able to take action immediately.",
    author: "Sarah Chen",
    role: "CEO",
    company: "TechCorp",
    rating: 5,
  },
  {
    quote:
      "The competitor gap alerts have been game-changing. We've caught 4 competitive moves early and defended our position every time.",
    author: "Michael Ross",
    role: "CTO",
    company: "InnovateLabs",
    rating: 5,
  },
  {
    quote:
      "Finally, a tool that actually measures GEO performance. The ROI was visible within the first month.",
    author: "Emily Stone",
    role: "VP Operations",
    company: "DataFlow",
    rating: 5,
  },
  {
    quote:
      "The market dynamic insights helped us identify a new competitor entering our space before they became a threat.",
    author: "David Kim",
    role: "Head of Marketing",
    company: "CloudSync",
    rating: 5,
  },
]

const logos = [
  { name: "TechCorp", color: "bg-blue-600" },
  { name: "InnovateLabs", color: "bg-indigo-600" },
  { name: "DataFlow", color: "bg-sky-600" },
  { name: "CloudSync", color: "bg-violet-600" },
  { name: "StartupHub", color: "bg-rose-600" },
  { name: "ScaleUp", color: "bg-emerald-600" },
]

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {[...Array(5)].map((_, i) => (
        <Star
          key={i}
          className={`h-4 w-4 ${i < rating ? "text-amber-400 fill-amber-400" : "text-slate-300"}`}
        />
      ))}
    </div>
  )
}

export default function TestimonialSection() {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const interval = setInterval(
      () => setCurrent((prev) => (prev + 1) % testimonials.length),
      5000,
    )
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="relative py-24 bg-slate-950 overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 right-[-10%] h-[380px] w-[380px] rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute bottom-[-20%] left-[-10%] h-[420px] w-[420px] rounded-full bg-sky-400/20 blur-3xl" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-blue-400 mb-4">
            Testimonials
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-white">
            Loved by Teams Everywhere
          </h2>
        </div>

        {/* Featured Testimonial with Video Option */}
        <div className="relative max-w-4xl mx-auto mb-16">
          <div className="bg-slate-900/80 p-8 md:p-12 rounded-3xl shadow-[0_28px_80px_-60px_rgba(15,23,42,0.9)] border border-slate-800/80 backdrop-blur-sm">
            {/* Quote Icon */}
            <div className="text-5xl text-blue-500 mb-4 font-serif">"</div>

            {/* Video Play Button (optional - for potential video testimonials) */}
            <button
              type="button"
              className="absolute top-8 right-8 w-12 h-12 rounded-full bg-blue-600/20 flex items-center justify-center hover:bg-blue-600/40 transition-colors group"
            >
              <Play className="h-5 w-5 text-blue-400 fill-blue-400 group-hover:scale-110 transition-transform" />
            </button>

            <div className="flex flex-col md:flex-row gap-8 items-start">
              {/* Quote Content */}
              <div className="flex-1">
                <p className="font-body text-lg leading-relaxed text-slate-200 mb-6 italic">
                  {testimonials[current].quote}
                </p>
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-sky-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
                    {testimonials[current].author.charAt(0)}
                  </div>
                  <div>
                    <div className="font-display font-semibold text-lg tracking-tight text-white">
                      {testimonials[current].author}
                    </div>
                    <div className="font-body text-sm text-slate-400">
                      {testimonials[current].role},{" "}
                      {testimonials[current].company}
                    </div>
                    <div className="mt-2">
                      <StarRating rating={testimonials[current].rating} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Dots */}
          <div className="flex justify-center gap-2 mt-6">
            {testimonials.map((_, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setCurrent(idx)}
                className={`w-2 h-2 rounded-full transition-all ${
                  current === idx
                    ? "w-8 bg-blue-500"
                    : "bg-slate-600 hover:bg-slate-500"
                }`}
                aria-label={`Go to testimonial ${idx + 1}`}
              />
            ))}
          </div>
        </div>

        {/* Company Logos */}
        <div>
          <h3 className="font-body font-medium text-xs tracking-[0.2em] uppercase text-center text-slate-400 mb-8">
            Trusted by leading companies worldwide
          </h3>
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-12">
            {logos.map((logo, idx) => (
              <div
                key={idx}
                className="group flex items-center gap-2 opacity-60 hover:opacity-100 transition-opacity"
              >
                <div
                  className={`w-8 h-8 rounded-lg ${logo.color} flex items-center justify-center`}
                >
                  <span className="text-white font-bold text-sm">
                    {logo.name.charAt(0)}
                  </span>
                </div>
                <span className="font-display font-medium text-sm tracking-[0.04em] text-slate-200">
                  {logo.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
