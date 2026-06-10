import { Link } from "@tanstack/react-router"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import type { PricingTier } from "@/lib/mock-data"

interface PricingCardProps {
  tier: PricingTier
}

export function PricingCard({ tier }: PricingCardProps) {
  return (
    <Card
      className={`p-6 flex flex-col h-full transition-all ${
        tier.highlighted
          ? "border-primary bg-primary/5 ring-2 ring-primary"
          : "hover:border-primary/50"
      }`}
    >
      <div className="flex-1">
        <h3 className="text-xl font-bold mb-2">{tier.name}</h3>
        <p className="text-foreground/60 text-sm mb-6">{tier.description}</p>

        <div className="mb-6">
          <span className="text-4xl font-bold">{tier.price}</span>
          <span className="text-foreground/60 ml-2">/month</span>
        </div>

        <ul className="space-y-3 mb-8">
          {tier.features.map((feature) => (
            <li key={feature} className="flex items-start gap-3">
              <Check className="w-5 h-5 text-accent shrink-0 mt-0.5" />
              <span className="text-sm text-foreground/70">{feature}</span>
            </li>
          ))}
        </ul>
      </div>

      <Link to="/dashboard">
        <Button
          className={`w-full ${tier.highlighted ? "bg-primary hover:bg-primary/90" : ""}`}
          variant={tier.highlighted ? "default" : "outline"}
        >
          {tier.cta}
        </Button>
      </Link>
    </Card>
  )
}
