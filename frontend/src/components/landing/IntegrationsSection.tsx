const integrations = [
  {
    name: "Google Gemini",
    logo: "https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg",
    bg: "bg-white",
    imgClass: "h-10 w-10 object-contain",
  },
  {
    name: "ChatGPT",
    logo: "https://cdn.jsdelivr.net/npm/simple-icons/icons/openai.svg",
    bg: "bg-[#10a37f]",
    imgClass: "h-8 w-8 object-contain invert",
  },
  {
    name: "Claude",
    logo: "https://cdn.simpleicons.org/anthropic",
    bg: "bg-[#D97757]",
    imgClass: "h-8 w-8 object-contain invert",
  },
  {
    name: "Perplexity",
    logo: "https://cdn.simpleicons.org/perplexity",
    bg: "bg-[#20808D]",
    imgClass: "h-8 w-8 object-contain invert",
  },
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
            Kila monitors your brand visibility across the AI platforms your
            customers use
          </p>
        </div>

        <div className="flex flex-wrap justify-center items-center gap-6">
          {integrations.map((integration) => (
            <div
              key={integration.name}
              className="group flex items-center gap-3 px-5 py-3.5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-lg hover:border-slate-300 transition-all duration-300 hover:-translate-y-1"
            >
              <div
                className={`flex-shrink-0 w-11 h-11 rounded-xl ${integration.bg} flex items-center justify-center border border-slate-100 overflow-hidden`}
              >
                <img
                  src={integration.logo}
                  alt={integration.name}
                  className={integration.imgClass}
                />
              </div>
              <span className="font-display font-semibold text-slate-900 whitespace-nowrap">
                {integration.name}
              </span>
            </div>
          ))}
        </div>

        <p className="text-center mt-8 text-sm text-slate-500">
          More platforms coming soon.{" "}
          <span className="text-blue-600 font-medium cursor-pointer hover:underline">
            Request a platform →
          </span>
        </p>
      </div>
    </section>
  )
}
