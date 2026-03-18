// src/components/landing/PricingSection.tsx

import { SignUpButton } from "@clerk/clerk-react"
import { Check, X } from "lucide-react"
import { useState } from "react"

interface Plan {
  name: string
  monthlyPrice: number
  yearlyPrice: number
  description: string
  features: string[]
  popular?: boolean
  cta: string
}

const plans: Plan[] = [
  {
    name: "Starter",
    monthlyPrice: 29,
    yearlyPrice: 24,
    description: "Perfect for small teams getting started with GEO",
    features: [
      "Up to 3 brands",
      "Basic analytics dashboard",
      "Daily AI visibility tracking",
      "Competitor basic tracking",
      "Email support",
      "5 data exports/month",
    ],
    cta: "Start Free Trial",
  },
  {
    name: "Professional",
    monthlyPrice: 99,
    yearlyPrice: 79,
    description: "For growing teams needing advanced insights",
    features: [
      "Up to 10 brands",
      "Advanced analytics & charts",
      "Real-time competitor alerts",
      "Sentiment analysis",
      "Priority email & chat support",
      "Unlimited data exports",
      "API access",
      "Custom segments",
    ],
    popular: true,
    cta: "Start Free Trial",
  },
  {
    name: "Enterprise",
    monthlyPrice: 0,
    yearlyPrice: 0,
    description: "For large organizations with custom needs",
    features: [
      "Unlimited brands",
      "Custom AI source monitoring",
      "Dedicated account manager",
      "24/7 phone support",
      "Custom integrations",
      "SLA guarantees",
      "Advanced security features",
      "On-premise deployment option",
    ],
    cta: "Contact Sales",
  },
]

const comparisonFeatures = [
  { name: "Brands", starter: "3", professional: "10", enterprise: "Unlimited" },
  {
    name: "Daily Tracking",
    starter: true,
    professional: true,
    enterprise: true,
  },
  {
    name: "Competitor Analysis",
    starter: "Basic",
    professional: "Advanced",
    enterprise: "Full",
  },
  {
    name: "Sentiment Analysis",
    starter: false,
    professional: true,
    enterprise: true,
  },
  {
    name: "Real-time Alerts",
    starter: false,
    professional: true,
    enterprise: true,
  },
  { name: "API Access", starter: false, professional: true, enterprise: true },
  {
    name: "Custom Segments",
    starter: false,
    professional: true,
    enterprise: true,
  },
  {
    name: "Priority Support",
    starter: false,
    professional: true,
    enterprise: true,
  },
  {
    name: "Dedicated Manager",
    starter: false,
    professional: false,
    enterprise: true,
  },
  {
    name: "SLA Guarantee",
    starter: false,
    professional: false,
    enterprise: true,
  },
]

function CheckIcon() {
  return (
    <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center">
      <Check className="h-3.5 w-3.5 text-emerald-600" />
    </div>
  )
}

function XIcon() {
  return (
    <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center">
      <X className="h-3.5 w-3.5 text-slate-400" />
    </div>
  )
}

function FeatureValue({ value }: { value: boolean | string }) {
  if (typeof value === "boolean") {
    return value ? <CheckIcon /> : <XIcon />
  }
  return <span className="text-sm font-medium text-slate-700">{value}</span>
}

export default function PricingSection() {
  const [isYearly, setIsYearly] = useState(false)
  const [showComparison, setShowComparison] = useState(false)

  return (
    <section
      id="pricing"
      className="relative py-24 bg-gradient-to-b from-white via-slate-50 to-white"
    >
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 right-[-10%] h-[380px] w-[380px] rounded-full bg-blue-500/10 blur-3xl" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="font-body text-base leading-relaxed text-slate-600 mb-8">
            Choose the plan that's right for you
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <span
              className={`text-sm font-medium ${!isYearly ? "text-slate-900" : "text-slate-500"}`}
            >
              Monthly
            </span>
            <button
              type="button"
              onClick={() => setIsYearly(!isYearly)}
              className={`
                relative w-14 h-7 rounded-full transition-colors
                ${isYearly ? "bg-blue-600" : "bg-slate-300"}
              `}
            >
              <span
                className={`
                  absolute top-1 w-5 h-5 bg-white rounded-full shadow
                  transition-transform duration-200
                  ${isYearly ? "translate-x-8" : "translate-x-1"}
                `}
              />
            </button>
            <span
              className={`text-sm font-medium ${isYearly ? "text-slate-900" : "text-slate-500"}`}
            >
              Yearly
            </span>
            {isYearly && (
              <span className="ml-2 px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-full">
                Save 20%
              </span>
            )}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`
                relative border-2 rounded-3xl p-8 transition-all duration-300
                ${
                  plan.popular
                    ? "border-blue-600 bg-white shadow-[0_28px_80px_-60px_rgba(37,99,235,0.6)] scale-105 hover:scale-107"
                    : "border-slate-200 bg-white shadow-[0_18px_60px_-50px_rgba(15,23,42,0.35)] hover:shadow-[0_25px_70px_-50px_rgba(15,23,42,0.45)] hover:border-slate-300"
                }
              `}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-600 to-blue-500 text-white px-4 py-1 rounded-full font-body font-medium text-xs tracking-[0.2em] uppercase shadow-lg">
                  Most Popular
                </div>
              )}
              <h3 className="font-display font-semibold text-2xl tracking-tight text-slate-900 mb-2">
                {plan.name}
              </h3>
              <p className="font-body text-sm text-slate-500 mb-6">
                {plan.description}
              </p>
              <div className="mb-6">
                {plan.monthlyPrice === 0 ? (
                  <div className="font-display font-bold text-4xl tracking-tight leading-[0.95] text-slate-900">
                    Custom
                  </div>
                ) : (
                  <>
                    <span className="font-display font-bold text-4xl tracking-tight leading-[0.95] text-slate-900">
                      ${isYearly ? plan.yearlyPrice : plan.monthlyPrice}
                    </span>
                    <span className="font-body text-base text-slate-600">
                      /month
                    </span>
                    {isYearly && (
                      <div className="text-xs text-slate-400 mt-1">
                        Billed ${plan.yearlyPrice * 12}/year
                      </div>
                    )}
                  </>
                )}
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li
                    key={i}
                    className="flex items-center font-body text-sm leading-relaxed text-slate-600"
                  >
                    <Check className="h-4 w-4 text-emerald-500 mr-2 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              <SignUpButton mode="modal" forceRedirectUrl="/app/brands">
                <button
                  type="button"
                  className={`
                    w-full py-3 rounded-xl font-body font-semibold transition-all
                    ${
                      plan.popular
                        ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 shadow-lg shadow-blue-500/25"
                        : "border-2 border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400"
                    }
                  `}
                >
                  {plan.cta}
                </button>
              </SignUpButton>
            </div>
          ))}
        </div>

        {/* Comparison Table Toggle */}
        <div className="text-center">
          <button
            type="button"
            onClick={() => setShowComparison(!showComparison)}
            className="text-blue-600 font-medium hover:underline"
          >
            {showComparison ? "Hide" : "Compare"} all features
          </button>
        </div>

        {/* Comparison Table */}
        {showComparison && (
          <div className="mt-8 overflow-x-auto">
            <table className="w-full min-w-[600px]">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-4 px-4 font-display font-semibold text-slate-900">
                    Features
                  </th>
                  <th className="text-center py-4 px-4 font-display font-semibold text-slate-900">
                    Starter
                  </th>
                  <th className="text-center py-4 px-4 font-display font-semibold text-blue-600 bg-blue-50 rounded-t-2xl">
                    Professional
                  </th>
                  <th className="text-center py-4 px-4 font-display font-semibold text-slate-900">
                    Enterprise
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisonFeatures.map((feature, idx) => (
                  <tr
                    key={idx}
                    className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
                  >
                    <td className="py-4 px-4 font-body text-sm text-slate-700">
                      {feature.name}
                    </td>
                    <td className="py-4 px-4 text-center">
                      <div className="flex justify-center">
                        <FeatureValue value={feature.starter} />
                      </div>
                    </td>
                    <td className="py-4 px-4 text-center bg-blue-50/50">
                      <div className="flex justify-center">
                        <FeatureValue value={feature.professional} />
                      </div>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <div className="flex justify-center">
                        <FeatureValue value={feature.enterprise} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}
