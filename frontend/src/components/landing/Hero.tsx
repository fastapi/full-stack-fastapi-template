// src/components/landing/Hero.tsx
interface HeroProps {
  onOpenAuth: (mode: 'signin' | 'signup') => void
}

export default function Hero({ onOpenAuth }: HeroProps) {
  return (
    <section className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 py-20">
      <div className="font-display max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          Transform Your Business with <span className="text-blue-600">SaaSPro</span>
        </h1>
        <p className="fond-display text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Streamline operations, boost productivity, and scale your business with our all-in-one platform
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => onOpenAuth('signup')}
            className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition font-semibold text-lg"
          >
            Start Free Trial
          </button>
          <button className="border-2 border-blue-600 text-blue-600 dark:text-blue-400 px-8 py-4 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-800 transition font-semibold text-lg">
            Watch Demo
          </button>
        </div>
      </div>
    </section>
  )
}
