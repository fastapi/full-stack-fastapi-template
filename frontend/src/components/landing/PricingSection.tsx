// src/components/landing/PricingSection.tsx
interface PricingSectionProps {
  onOpenAuth: (mode: 'signin' | 'signup') => void
}

export default function PricingSection({ onOpenAuth }: PricingSectionProps) {
  const plans = [
    {
      name: 'Starter',
      price: '$29',
      features: ['Up to 10 users', 'Basic analytics', 'Email support', '5GB storage']
    },
    {
      name: 'Professional',
      price: '$99',
      popular: true,
      features: ['Up to 50 users', 'Advanced analytics', 'Priority support', '100GB storage', 'API access']
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      features: ['Unlimited users', 'Custom analytics', '24/7 phone support', 'Unlimited storage', 'Dedicated account manager']
    }
  ]

  return (
    <section id="pricing" className="py-20 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4 text-center">
          Simple, Transparent Pricing
        </h2>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 text-center">
          Choose the plan that's right for you
        </p>

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`border ${plan.popular ? 'border-blue-600 ring-2 ring-blue-600' : 'border-gray-200 dark:border-gray-700'} rounded-xl p-8 relative`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{plan.name}</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900 dark:text-white">{plan.price}</span>
                {plan.price !== 'Custom' && <span className="text-gray-600 dark:text-gray-400">/month</span>}
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center text-gray-600 dark:text-gray-300">
                    <span className="text-green-500 mr-2">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => onOpenAuth('signup')}
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  plan.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
