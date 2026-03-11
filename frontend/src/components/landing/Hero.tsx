// src/components/landing/Hero.tsx
import { SignUpButton } from "@clerk/clerk-react"
import { Button } from "@/components/ui/button.tsx"

export default function Hero() {
  return (
    <section className="bg-gradient-to-br from-slate-50 via-white to-sky-50 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="font-display font-bold text-4xl sm:text-5xl md:text-6xl tracking-tight leading-[1.05] text-slate-900 dark:text-white mb-6">
          Turn AI Search Into Growth Intelligence
        </h1>
        <p className="font-body text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed mb-10 max-w-3xl mx-auto">
          AI Search Intelligence for Market Leaders. Detect Shifts. Defend
          Share. Drive Growth.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <SignUpButton mode="modal" forceRedirectUrl="/app/projects">
            <Button size={"lg"}>Start Free Trial</Button>
          </SignUpButton>
          <Button variant={"outline"} size="lg">
            Watch Demo
          </Button>
        </div>
      </div>
    </section>
  )
}
