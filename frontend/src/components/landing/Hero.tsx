// src/components/landing/Hero.tsx
import { SignUpButton } from "@clerk/clerk-react"
import { Button } from "@/components/ui/button.tsx"

export default function Hero() {
  return (
    <section className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 py-20">
      <div className="font-display max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          Transform Your Business with{" "}
          <span className="text-blue-600">Kila</span>
        </h1>
        <p className="fond-display text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Streamline operations, boost productivity, and scale your business
          with our all-in-one platform
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
