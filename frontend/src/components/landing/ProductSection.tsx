import { BarChart3, Users, Zap } from "lucide-react"

export default function ProductSection() {
  const products = [
    {
      icon: BarChart3,
      title: "Analytics Dashboard",
      description:
        "Real-time insights and powerful analytics to make data-driven decisions",
      accent: "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300",
    },
    {
      icon: Zap,
      title: "Automation Engine",
      description:
        "Automate repetitive tasks and workflows to save time and reduce errors",
      accent:
        "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300",
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description:
        "Connect your team with seamless communication and project management",
      accent: "bg-sky-50 text-sky-600 dark:bg-sky-900/30 dark:text-sky-300",
    },
  ]

  return (
    <section className="py-20 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900 dark:text-white mb-4">
            Our Products
          </h2>
          <p className="font-body text-base text-slate-600 dark:text-slate-300 leading-relaxed">
            Everything you need to succeed
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8">
          {products.map((product, idx) => {
            const Icon = product.icon
            return (
              <div
                key={idx}
                className="bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 p-8 rounded-2xl shadow-sm hover:shadow-lg transition"
              >
                <div
                  className={`h-11 w-11 rounded-2xl flex items-center justify-center ${product.accent} mb-4`}
                >
                  <Icon size={20} />
                </div>
                <h3 className="font-display font-semibold text-2xl tracking-tight text-slate-900 dark:text-white mb-3">
                  {product.title}
                </h3>
                <p className="font-body text-base leading-relaxed text-slate-600 dark:text-slate-300">
                  {product.description}
                </p>
              </div>
            )
          })}
        </div>

        <div className="mt-12 sm:mt-20 bg-gradient-to-r from-blue-600 to-sky-500 rounded-2xl p-6 sm:p-10 lg:p-12 text-white">
          <h3 className="font-display font-bold text-2xl sm:text-4xl tracking-tight mb-6 sm:mb-8 text-center">
            Why Customers Choose Us
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8">
            <div className="text-center">
              <div className="font-display font-bold text-4xl sm:text-5xl tracking-tight leading-[0.95] mb-2">
                10x
              </div>
              <div className="font-body text-xs uppercase tracking-[0.2em] text-blue-100">
                Faster Workflows
              </div>
            </div>
            <div className="text-center">
              <div className="font-display font-bold text-4xl sm:text-5xl tracking-tight leading-[0.95] mb-2">
                99.9%
              </div>
              <div className="font-body text-xs uppercase tracking-[0.2em] text-blue-100">
                Uptime Guarantee
              </div>
            </div>
            <div className="text-center">
              <div className="font-display font-bold text-4xl sm:text-5xl tracking-tight leading-[0.95] mb-2">
                24/7
              </div>
              <div className="font-body text-xs uppercase tracking-[0.2em] text-blue-100">
                Expert Support
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
