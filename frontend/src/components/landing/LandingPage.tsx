import FAQSection from "./FAQSection"
import FeatureGridSection from "./FeatureGridSection"
import FinalCTASection from "./FinalCTASection"
import Footer from "./Footer"
import Header from "./Header"
import Hero from "./Hero"
import HowItWorksSection from "./HowItWorksSection"
import IntegrationsSection from "./IntegrationsSection"
import PricingSection from "./PricingSection"
import ProductSection from "./ProductSection"
import SecuritySection from "./SecuritySection"
import StatsSection from "./StatsSection"
import TestimonialSection from "./TestimonialSection"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main>
        <Hero />
        <StatsSection />
        <FeatureGridSection />
        <ProductSection />
        <IntegrationsSection />
        <HowItWorksSection />
        <SecuritySection />
        <TestimonialSection />
        <FAQSection />
        <PricingSection />
        <FinalCTASection />
      </main>

      <Footer />
    </div>
  )
}