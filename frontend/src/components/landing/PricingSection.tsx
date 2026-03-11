// src/components/landing/PricingSection.tsx
import { SignUpButton } from "@clerk/clerk-react"
import { Check } from "lucide-react"

export default function PricingSection() {
  const plans = [
    {
      name: "Starter",
      price: "$29",
      features: [
        "Up to 10 users",
        "Basic analytics",
        "Email support",
        "5GB storage",
      ],
    },
    {
      name: "Professional",
      price: "$99",
      popular: true,
      features: [
        "Up to 50 users",
        "Advanced analytics",
        "Priority support",
        "100GB storage",
        "API access",
      ],
    },
    {
      name: "Enterprise",
      price: "Custom",
      features: [
        "Unlimited users",
        "Custom analytics",
        "24/7 phone support",
        "Unlimited storage",
        "Dedicated account manager",
      ],
    },
  ]

  return (
    <section id="pricing" className="py-20 bg-slate-50 dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900 dark:text-white mb-4 text-center">
          Simple, Transparent Pricing
        </h2>
        <p className="font-body text-base leading-relaxed text-slate-600 dark:text-slate-300 mb-12 text-center">
          Choose the plan that's right for you
        </p>

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`border ${plan.popular ? "border-blue-600 bg-white dark:bg-slate-900 shadow-lg" : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900"} rounded-2xl p-8 relative`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-1 rounded-full font-body font-medium text-xs tracking-[0.2em] uppercase">
                  Most Popular
                </div>
              )}
              <h3 className="font-display font-semibold text-2xl tracking-tight text-slate-900 dark:text-white mb-2">
                {plan.name}
              </h3>
              <div className="mb-6">
                <span className="font-display font-bold text-4xl tracking-tight leading-[0.95] text-slate-900 dark:text-white">
                  {plan.price}
                </span>
                {plan.price !== "Custom" && (
                  <span className="font-body text-base text-slate-600 dark:text-slate-400">
                    /month
                  </span>
                )}
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li
                    key={i}
                    className="flex items-center font-body text-base leading-relaxed text-slate-600 dark:text-slate-300"
                  >
                    <Check className="h-4 w-4 text-emerald-500 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
              <SignUpButton mode="modal" forceRedirectUrl="/app/projects">
                <button
                  type="button"
                  className={`w-full py-3 rounded-xl font-body font-semibold transition ${
                    plan.popular
                      ? "bg-blue-600 text-white hover:bg-blue-700"
                      : "border-2 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                  }`}
                >
                  Get Started
                </button>
              </SignUpButton>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
