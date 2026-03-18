import {
  Eye,
  Target,
  TrendingUp,
  AlertTriangle,
  BarChart3,
  Users,
} from "lucide-react"

const features = [
  {
    icon: Eye,
    title: "AI Visibility Tracking",
    description: "Monitor how your brand appears in AI search results across all major platforms",
    color: "blue",
  },
  {
    icon: Target,
    title: "Competitor Gap Analysis",
    description: "Compare your visibility against competitors and spot displacement early",
    color: "indigo",
  },
  {
    icon: TrendingUp,
    title: "Market Dynamic",
    description: "Track category shifts, visibility volatility, and emerging market patterns",
    color: "sky",
  },
  {
    icon: AlertTriangle,
    title: "Risk Intelligence",
    description: "Early warning signals before your visibility drops or competitors gain ground",
    color: "rose",
  },
  {
    icon: BarChart3,
    title: "Segment Insights",
    description: "Drill down into specific market segments for targeted analysis",
    color: "violet",
  },
  {
    icon: Users,
    title: "Multi-Brand Support",
    description: "Manage and compare multiple brands from a single dashboard",
    color: "emerald",
  },
]

const colorClasses = {
  blue: { bg: "bg-blue-50", text: "text-blue-600", border: "border-blue-200", hover: "hover:border-blue-300 hover:bg-blue-50" },
  indigo: { bg: "bg-indigo-50", text: "text-indigo-600", border: "border-indigo-200", hover: "hover:border-indigo-300 hover:bg-indigo-50" },
  sky: { bg: "bg-sky-50", text: "text-sky-600", border: "border-sky-200", hover: "hover:border-sky-300 hover:bg-sky-50" },
  rose: { bg: "bg-rose-50", text: "text-rose-600", border: "border-rose-200", hover: "hover:border-rose-300 hover:bg-rose-50" },
  violet: { bg: "bg-violet-50", text: "text-violet-600", border: "border-violet-200", hover: "hover:border-violet-300 hover:bg-violet-50" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600", border: "border-emerald-200", hover: "hover:border-emerald-300 hover:bg-emerald-50" },
}

export default function FeatureGridSection() {
  return (
    <section className="relative py-24 bg-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-3xl" />
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-blue-600 mb-4">
            Features
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900">
            Everything You Need to Master AI Visibility
          </h2>
          <p className="font-body text-base text-slate-600 mt-4 max-w-2xl mx-auto">
            Comprehensive tools to track, analyze, and optimize your brand's presence in AI search results
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => {
            const colors = colorClasses[feature.color as keyof typeof colorClasses]
            return (
              <div
                key={idx}
                className={`
                  group relative p-6 rounded-2xl border-2 transition-all duration-300 cursor-pointer
                  ${colors.border} bg-white
                  hover:shadow-xl hover:-translate-y-1
                  ${colors.hover}
                `}
              >
                {/* Icon */}
                <div className={`
                  relative w-14 h-14 rounded-2xl ${colors.bg} flex items-center justify-center mb-4
                  group-hover:scale-110 transition-transform duration-300
                `}>
                  <feature.icon className={`h-7 w-7 ${colors.text}`} />
                </div>

                {/* Content */}
                <h3 className="font-display font-semibold text-lg text-slate-900 mb-2">
                  {feature.title}
                </h3>
                <p className="font-body text-sm text-slate-600 leading-relaxed">
                  {feature.description}
                </p>

                {/* Arrow indicator */}
                <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:translate-x-1">
                  <svg className={`w-5 h-5 ${colors.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}