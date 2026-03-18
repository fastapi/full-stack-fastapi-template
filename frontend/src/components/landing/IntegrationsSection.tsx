import { Bot, Sparkles, MessageSquare, Search, Cpu } from "lucide-react"

const integrations = [
  { name: "Google Gemini", icon: Sparkles, color: "from-blue-400 to-blue-600" },
  { name: "ChatGPT", icon: Bot, color: "from-green-400 to-green-600" },
  { name: "Claude", icon: MessageSquare, color: "from-orange-400 to-orange-600" },
  { name: "Microsoft Copilot", icon: Search, color: "from-violet-400 to-violet-600" },
  { name: "Perplexity", icon: Cpu, color: "from-red-400 to-red-600" },
]

export default function IntegrationsSection() {
  return (
    <section className="relative py-20 bg-slate-50">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/5 rounded-full blur-3xl" />
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-blue-600 mb-4">
            Integrations
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900">
            Works With All Major AI Platforms
          </h2>
          <p className="font-body text-base text-slate-600 mt-4 max-w-2xl mx-auto">
            Kila monitors your brand visibility across the AI platforms your customers use
          </p>
        </div>

        <div className="flex flex-wrap justify-center items-center gap-8">
          {integrations.map((integration, idx) => (
            <div
              key={idx}
              className="group relative flex items-center gap-3 px-6 py-4 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-lg hover:border-slate-300 transition-all duration-300 hover:-translate-y-1"
            >
              <div className={`
                w-12 h-12 rounded-xl bg-gradient-to-br ${integration.color}
                flex items-center justify-center
              `}>
                <integration.icon className="h-6 w-6 text-white" />
              </div>
              <span className="font-display font-semibold text-slate-900">
                {integration.name}
              </span>
            </div>
          ))}
        </div>

        <p className="text-center mt-8 text-sm text-slate-500">
          More platforms coming soon. <span className="text-blue-600 font-medium">Request a platform →</span>
        </p>
      </div>
    </section>
  )
}