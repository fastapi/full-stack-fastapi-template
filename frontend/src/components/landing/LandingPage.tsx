import Footer from "./Footer"
import Header from "./Header"
import Hero from "./Hero"
import PricingSection from "./PricingSection"
import ProductSection from "./ProductSection"
import TestimonialSection from "./TestimonialSection"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Header />

      <main>
        <Hero />
        <ProductSection />
        <TestimonialSection />
        <PricingSection />
      </main>

      <Footer />
    </div>
  )
}
