// src/components/landing/PricingSection.tsx

import { SignUpButton } from "@clerk/clerk-react"
import { Check, X } from "lucide-react"
import { useState } from "react"

interface Plan {
  name: string
  price: number | null
  description: string
  features: string[]
  popular?: boolean
  cta: string
  ctaVariant?: "primary" | "outline" | "contact"
}

const plans: Plan[] = [
  {
    name: "Free Trial",
    price: 0,
    description: "4 weeks free — no credit card required",
    features: [
      "1 active brand",
      "1 segment",
      "1 model result",
      "Daily AI search visibility tracking",
      "Brand impression dashboard",
      "Ranking & citation monitoring",
      "Basic competitive comparison",
      "Segment-level prompt setup",
      "Email support",
    ],
    cta: "Start Free Trial",
    ctaVariant: "outline",
  },
  {
    name: "Pro",
    price: 299,
    description: "Full AI search intelligence for growth teams",
    features: [
      "1 active brand",
      "3 segments under active brand",
      "3 models results",
      "Everything in Free Trial",
      "Advanced competitive analysis",
      "Market dynamic insights",
      "Risk intelligence & early-warning alerts",
      "Multi-model AI tracking",
      "Competitor breakthrough detection",
      "Priority support",
    ],
    popular: true,
    cta: "Get Pro — 4 Weeks Free",
    ctaVariant: "primary",
  },
  {
    name: "Enterprise",
    price: null,
    description: "Custom scale for larger organizations",
    features: [
      "Multiple brands",
      "Everything in Pro",
      "Custom AI source monitoring",
      "Dedicated account manager",
      "Custom integrations & API access",
      "SLA guarantees",
      "Advanced security & compliance",
      "24/7 priority support",
    ],
    cta: "Contact Sales",
    ctaVariant: "contact",
  },
]

const comparisonFeatures = [
  { name: "Active brands", free: "1", pro: "1", enterprise: "Multiple" },
  { name: "Segments", free: "1", pro: "3", enterprise: "3" },
  {
    name: "Daily AI visibility tracking",
    free: true,
    pro: true,
    enterprise: true,
  },
  {
    name: "Brand impression dashboard",
    free: true,
    pro: true,
    enterprise: true,
  },
  {
    name: "Ranking & citation monitoring",
    free: true,
    pro: true,
    enterprise: true,
  },
  {
    name: "Competitive comparison",
    free: "Basic",
    pro: "Advanced",
    enterprise: "Full",
  },
  { name: "Market dynamic insights", free: false, pro: true, enterprise: true },
  {
    name: "Risk intelligence alerts",
    free: false,
    pro: true,
    enterprise: true,
  },
  { name: "Multi-model AI tracking", free: false, pro: true, enterprise: true },
  { name: "API access", free: false, pro: false, enterprise: true },
  { name: "Custom integrations", free: false, pro: false, enterprise: true },
  {
    name: "Dedicated account manager",
    free: false,
    pro: false,
    enterprise: true,
  },
  { name: "SLA guarantee", free: false, pro: false, enterprise: true },
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
          <p className="font-body text-base leading-relaxed text-slate-600">
            Start free for 4 weeks — no credit card required
          </p>
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
                    ? "border-blue-600 bg-white shadow-[0_28px_80px_-60px_rgba(37,99,235,0.6)] scale-105"
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
                {plan.price === null ? (
                  <div className="font-display font-bold text-4xl tracking-tight leading-[0.95] text-slate-900">
                    Custom
                  </div>
                ) : plan.price === 0 ? (
                  <div className="font-display font-bold text-4xl tracking-tight leading-[0.95] text-slate-900">
                    Free
                    <span className="font-body text-base text-slate-500 ml-1">
                      / 4 weeks
                    </span>
                  </div>
                ) : (
                  <>
                    <span className="font-display font-bold text-4xl tracking-tight leading-[0.95] text-slate-900">
                      ${plan.price}
                    </span>
                    <span className="font-body text-base text-slate-600">
                      /month
                    </span>
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
              {plan.ctaVariant === "contact" ? (
                <a
                  href="mailto:hello@kila.ai"
                  className="block w-full py-3 rounded-xl font-body font-semibold text-center transition-all border-2 border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400"
                >
                  {plan.cta}
                </a>
              ) : (
                <SignUpButton
                  mode="modal"
                  {...(plan.name === "Pro"
                    ? { forceRedirectUrl: "/app/onboarding?plan=pro" }
                    : { forceRedirectUrl: "/app/brands" })}
                >
                  <button
                    type="button"
                    className={`
                      w-full py-3 rounded-xl font-body font-semibold transition-all
                      ${
                        plan.ctaVariant === "primary"
                          ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 shadow-lg shadow-blue-500/25"
                          : "border-2 border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400"
                      }
                    `}
                  >
                    {plan.cta}
                  </button>
                </SignUpButton>
              )}
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
                    Free Trial
                  </th>
                  <th className="text-center py-4 px-4 font-display font-semibold text-blue-600 bg-blue-50 rounded-t-2xl">
                    Pro
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
                        <FeatureValue value={feature.free} />
                      </div>
                    </td>
                    <td className="py-4 px-4 text-center bg-blue-50/50">
                      <div className="flex justify-center">
                        <FeatureValue value={feature.pro} />
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
