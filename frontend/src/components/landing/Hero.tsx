// src/components/landing/Hero.tsx
import { SignUpButton } from "@clerk/clerk-react"
import { Button } from "@/components/ui/button.tsx"

export default function Hero() {
  return (
    <section className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="font-funnel-sans font-extrabold text-2xl sm:text-3xl md:text-[48px] tracking-[-0.04em] leading-[0.9] text-gray-900 dark:text-white mb-6">
          Turn AI Search Into Growth Intelligence
        </h1>
        <p className="font-funnel-sans font-normal text-base sm:text-lg text-gray-600 dark:text-gray-300 leading-[1.7] opacity-75 mb-8 max-w-3xl mx-auto">
          AI Search Intelligence for Market Leaders. Detect Shifts. Defend Share. Drive Growth.
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
