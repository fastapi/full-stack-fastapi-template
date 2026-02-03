import { useState } from 'react'
import Header from './Header'
import Hero from './Hero'
import ProductSection from './ProductSection'
import TestimonialSection from './TestimonialSection'
import PricingSection from './PricingSection'
import Footer from './Footer'
import AuthDialog from './AuthDialog'

export default function LandingPage() {
  const [authDialogOpen, setAuthDialogOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin')

  const openAuthDialog = (mode: 'signin' | 'signup') => {
    setAuthMode(mode)
    setAuthDialogOpen(true)
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Header onOpenAuth={openAuthDialog} />

      <main>
        <Hero onOpenAuth={openAuthDialog} />
        <ProductSection />
        <TestimonialSection />
        <PricingSection onOpenAuth={openAuthDialog} />
      </main>

      <Footer />

      <AuthDialog
        open={authDialogOpen}
        onOpenChange={setAuthDialogOpen}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </div>
  )
}