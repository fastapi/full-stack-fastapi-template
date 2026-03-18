import { SignUpButton } from "@clerk/clerk-react"
import { Button } from "@/components/ui/button"

export default function FinalCTASection() {
  return (
    <section className="relative py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-sky-500/10 rounded-full blur-3xl" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
      </div>
      
      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="font-display font-bold text-3xl sm:text-4xl md:text-5xl tracking-tight text-white mb-6">
          Ready to Master Your AI Visibility?
        </h2>
        <p className="font-body text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
          Join 500+ brands already tracking their AI search presence. 
          Start your free 14-day trial — no credit card required.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <SignUpButton mode="modal" forceRedirectUrl="/app/brands">
            <Button
              size="lg"
              className="bg-gradient-to-r from-blue-600 to-sky-500 hover:from-blue-700 hover:to-sky-600 text-white shadow-lg shadow-blue-500/25 px-8"
            >
              Start Free Trial
            </Button>
          </SignUpButton>
          <Button
            variant="outline"
            size="lg"
            className="border-slate-600 text-white hover:bg-slate-800 hover:border-slate-500 px-8"
          >
            Book a Demo
          </Button>
        </div>

        <p className="mt-6 text-sm text-slate-400">
          ✓ No credit card required &nbsp; ✓ 14-day free trial &nbsp; ✓ Cancel anytime
        </p>
      </div>
    </section>
  )
}