import { CheckCircle2, LineChart, Search, Settings } from "lucide-react"

const steps = [
  {
    number: "01",
    icon: Search,
    title: "Connect Your Brand",
    description:
      "Add your brand and define the segments you want to track. We'll immediately start monitoring your AI visibility.",
    color: "blue",
  },
  {
    number: "02",
    icon: LineChart,
    title: "Monitor & Analyze",
    description:
      "Track daily AI search results, competitor movements, and market shifts. Get comprehensive visibility metrics.",
    color: "indigo",
  },
  {
    number: "03",
    icon: Settings,
    title: "Optimize & Act",
    description:
      "Receive actionable insights and alerts. Make data-driven decisions to improve your AI search presence.",
    color: "sky",
  },
]

const colorClasses = {
  blue: {
    bg: "bg-blue-50",
    text: "text-blue-600",
    border: "border-blue-200",
    gradient: "from-blue-500 to-blue-600",
    glow: "hover:shadow-blue-500/25",
  },
  indigo: {
    bg: "bg-indigo-50",
    text: "text-indigo-600",
    border: "border-indigo-200",
    gradient: "from-indigo-500 to-indigo-600",
    glow: "hover:shadow-indigo-500/25",
  },
  sky: {
    bg: "bg-sky-50",
    text: "text-sky-600",
    border: "border-sky-200",
    gradient: "from-sky-500 to-sky-600",
    glow: "hover:shadow-sky-500/25",
  },
}

export default function HowItWorksSection() {
  return (
    <section className="relative py-24 bg-slate-50">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-blue-600 mb-4">
            How It Works
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900">
            Three Steps to AI Visibility Success
          </h2>
          <p className="font-body text-base text-slate-600 mt-4 max-w-2xl mx-auto">
            Get started in minutes and start optimizing your AI search presence
          </p>
        </div>

        <div className="relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 -translate-y-1/2 bg-gradient-to-r from-blue-200 via-indigo-200 to-sky-200" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, idx) => {
              const colors =
                colorClasses[step.color as keyof typeof colorClasses]
              return (
                <div key={idx} className="relative group">
                  <div
                    className={`
                    relative bg-white rounded-3xl p-8 border-2 
                    ${colors.border} shadow-lg hover:shadow-xl 
                    transition-all duration-500 ${colors.glow}
                    hover:-translate-y-2
                  `}
                  >
                    {/* Step number */}
                    <div
                      className={`
                      absolute -top-4 left-8 px-4 py-1 
                      bg-gradient-to-r ${colors.gradient}
                      rounded-full text-white text-xs font-bold
                    `}
                    >
                      {step.number}
                    </div>

                    {/* Icon */}
                    <div
                      className={`
                      relative w-16 h-16 rounded-2xl 
                      ${colors.bg} flex items-center justify-center
                      mb-6 group-hover:scale-110 transition-transform duration-300
                    `}
                    >
                      <div
                        className={`
                        absolute inset-0 rounded-2xl 
                        bg-gradient-to-r ${colors.gradient}
                        opacity-0 group-hover:opacity-10 transition-opacity
                      `}
                      />
                      <step.icon className={`h-8 w-8 ${colors.text}`} />
                    </div>

                    {/* Content */}
                    <h3 className="font-display font-semibold text-xl text-slate-900 mb-3">
                      {step.title}
                    </h3>
                    <p className="font-body text-sm text-slate-600 leading-relaxed">
                      {step.description}
                    </p>

                    {/* Checkmark for completed feel */}
                    <div className="absolute bottom-8 right-8 opacity-0 group-hover:opacity-100 transition-opacity">
                      <CheckCircle2 className={`h-6 w-6 ${colors.text}`} />
                    </div>
                  </div>

                  {/* Arrow between steps (hidden on last) */}
                  {idx < steps.length - 1 && (
                    <div className="hidden md:block absolute top-1/2 -right-4 -translate-y-1/2 z-10">
                      <div className="w-8 h-8 bg-white rounded-full border-2 border-slate-200 flex items-center justify-center">
                        <svg
                          className="w-4 h-4 text-slate-400"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          aria-hidden="true"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
