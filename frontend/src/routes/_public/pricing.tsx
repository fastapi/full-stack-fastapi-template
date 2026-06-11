import { createFileRoute, Link } from "@tanstack/react-router"
import { Check, HelpCircle, Zap } from "lucide-react"
import { useState } from "react"
import Footer from "@/components/footer"
import Header from "@/components/header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { pricingTiers } from "@/lib/mock-data"

export const Route = createFileRoute("/_public/pricing")({
  component: PricingPage,
  head: () => ({
    meta: [{ title: "Pricing – BankToExcel" }],
  }),
})

const ANNUAL_DISCOUNT = 0.2 // 20% off when billed annually

function getAnnualPrice(monthlyPrice: string): string {
  if (monthlyPrice === "$0") return "$0"
  const num = Number.parseFloat(monthlyPrice.replace("$", ""))
  if (Number.isNaN(num)) return monthlyPrice
  const annual = (num * (1 - ANNUAL_DISCOUNT)).toFixed(2)
  return `$${annual}`
}

const faqs = [
  {
    q: "Can I change my plan later?",
    a: "Yes, you can upgrade or downgrade at any time. Changes take effect immediately and we'll prorate any billing differences.",
  },
  {
    q: "Is there a free trial?",
    a: "Every paid plan includes a 7-day free trial. No credit card required to start.",
  },
  {
    q: "What file formats do you support?",
    a: "We support PDF, JPG, PNG, and other common image formats. Scanned documents and digital PDFs both work.",
  },
  {
    q: "How accurate are the conversions?",
    a: "Our AI achieves 99%+ accuracy on clearly formatted bank statements from most major banks.",
  },
  {
    q: "Can I cancel anytime?",
    a: "Absolutely. Cancel with one click from your account settings — no cancellation fees.",
  },
  {
    q: "Do you offer team plans?",
    a: "The Business plan includes up to 5 seats. Need more? Contact us for a custom quote.",
  },
]

function PricingPage() {
  const [annual, setAnnual] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero */}
      <section className="py-16 px-4 text-center">
        <Badge
          variant="outline"
          className="mb-4 gap-1.5 px-3 py-1 text-xs font-medium"
        >
          <Zap className="h-3 w-3 text-primary" />
          Simple, transparent pricing
        </Badge>
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
          Plans for every workflow
        </h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-xl mx-auto">
          Convert bank statements to Excel in seconds. Start free, upgrade when
          you need more.
        </p>

        {/* Billing toggle */}
        <div className="mt-8 inline-flex items-center gap-3 rounded-full border border-border bg-muted p-1">
          <button
            type="button"
            onClick={() => setAnnual(false)}
            className={`rounded-full px-5 py-1.5 text-sm font-medium transition-all ${
              !annual
                ? "bg-background text-foreground shadow"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Monthly
          </button>
          <button
            type="button"
            onClick={() => setAnnual(true)}
            className={`flex items-center gap-2 rounded-full px-5 py-1.5 text-sm font-medium transition-all ${
              annual
                ? "bg-background text-foreground shadow"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Annual
            <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
              Save 20%
            </span>
          </button>
        </div>
      </section>

      {/* Pricing cards */}
      <section className="px-4 pb-20">
        <div className="mx-auto max-w-6xl grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {pricingTiers.map((tier) => {
            const displayPrice = annual
              ? getAnnualPrice(tier.price)
              : tier.price
            const isFree = tier.price === "$0"

            return (
              <Card
                key={tier.name}
                className={`relative flex flex-col p-8 transition-all ${
                  tier.highlighted
                    ? "border-primary ring-2 ring-primary bg-primary/5 shadow-lg"
                    : "hover:border-primary/40"
                }`}
              >
                {tier.highlighted && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <Badge className="px-4 py-1 text-xs font-semibold shadow">
                      Most Popular
                    </Badge>
                  </div>
                )}

                <div className="flex-1">
                  <h2 className="text-xl font-bold">{tier.name}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {tier.description}
                  </p>

                  <div className="mt-6 flex items-end gap-1">
                    <span className="text-5xl font-extrabold tracking-tight">
                      {displayPrice}
                    </span>
                    {!isFree && (
                      <span className="mb-1.5 text-muted-foreground text-sm">
                        /mo{annual ? ", billed annually" : ""}
                      </span>
                    )}
                  </div>

                  {annual && !isFree && (
                    <p className="mt-1 text-xs text-muted-foreground line-through">
                      {tier.price}/mo
                    </p>
                  )}

                  <ul className="mt-8 space-y-3">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <span className="text-sm text-foreground/75">
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-8">
                  <Link to={isFree ? "/signup" : "/signup"}>
                    <Button
                      className="w-full"
                      variant={tier.highlighted ? "default" : "outline"}
                      size="lg"
                    >
                      {tier.cta}
                    </Button>
                  </Link>
                  {!isFree && (
                    <p className="mt-3 text-center text-xs text-muted-foreground">
                      7-day free trial · No credit card required
                    </p>
                  )}
                </div>
              </Card>
            )
          })}
        </div>
      </section>

      {/* Feature comparison table */}
      <section className="border-t border-border px-4 py-20 bg-muted/30">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-center text-3xl font-bold mb-12">
            Compare plans
          </h2>
          <div className="overflow-x-auto rounded-xl border border-border bg-background shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="p-4 text-left font-semibold text-foreground w-1/2">
                    Feature
                  </th>
                  {pricingTiers.map((t) => (
                    <th
                      key={t.name}
                      className={`p-4 text-center font-semibold ${
                        t.highlighted ? "text-primary" : "text-foreground"
                      }`}
                    >
                      {t.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {[
                  {
                    label: "Conversions / month",
                    values: ["5", "100", "Unlimited"],
                  },
                  {
                    label: "Max file size",
                    values: ["5 MB", "50 MB", "100 MB"],
                  },
                  { label: "PDF support", values: [true, true, true] },
                  { label: "Image support", values: [true, true, true] },
                  { label: "Advanced formatting", values: [false, true, true] },
                  {
                    label: "Transaction categorization",
                    values: [false, true, true],
                  },
                  { label: "Custom templates", values: [false, false, true] },
                  { label: "Batch processing", values: [false, false, true] },
                  { label: "API access", values: [false, false, true] },
                  { label: "Team seats", values: ["—", "1", "Up to 5"] },
                  {
                    label: "Download history",
                    values: ["—", "30 days", "Unlimited"],
                  },
                  {
                    label: "Support",
                    values: ["Email", "Priority email", "Priority + SLA"],
                  },
                ].map((row) => (
                  <tr
                    key={row.label}
                    className="hover:bg-muted/50 transition-colors"
                  >
                    <td className="p-4 text-foreground/80">{row.label}</td>
                    {row.values.map((val, i) => (
                      <td
                        key={`${row.label}-${pricingTiers[i].name}`}
                        className="p-4 text-center"
                      >
                        {typeof val === "boolean" ? (
                          val ? (
                            <Check className="mx-auto h-4 w-4 text-primary" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-foreground/80">{val}</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="px-4 py-20">
        <div className="mx-auto max-w-3xl">
          <h2 className="text-center text-3xl font-bold mb-12">
            Frequently asked questions
          </h2>
          <div className="space-y-4">
            {faqs.map((item) => (
              <div
                key={item.q}
                className="rounded-xl border border-border bg-card p-6"
              >
                <div className="flex items-start gap-3">
                  <HelpCircle className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                  <div>
                    <p className="font-semibold text-foreground">{item.q}</p>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                      {item.a}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA banner */}
      <section className="border-t border-border px-4 py-20 bg-primary/5">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold">
            Ready to save hours every month?
          </h2>
          <p className="mt-4 text-muted-foreground">
            Join thousands of accountants who use BankToExcel to convert
            statements in seconds — not hours.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" className="px-8">
                Start for free
              </Button>
            </Link>
            <Link to="/">
              <Button size="lg" variant="outline" className="px-8">
                See how it works
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
