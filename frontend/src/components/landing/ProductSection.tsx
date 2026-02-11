export default function ProductSection() {
  const products = [
    {
      icon: "📊",
      title: "Analytics Dashboard",
      description:
        "Real-time insights and powerful analytics to make data-driven decisions",
      color:
        "from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20",
    },
    {
      icon: "⚡",
      title: "Automation Engine",
      description:
        "Automate repetitive tasks and workflows to save time and reduce errors",
      color:
        "from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20",
    },
    {
      icon: "🤝",
      title: "Team Collaboration",
      description:
        "Connect your team with seamless communication and project management",
      color:
        "from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20",
    },
  ]

  return (
    <section className="py-20 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Our Products
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Everything you need to succeed
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {products.map((product, idx) => (
            <div
              key={idx}
              className={`bg-gradient-to-br ${product.color} p-8 rounded-xl hover:shadow-lg transition`}
            >
              <div className="text-4xl mb-4">{product.icon}</div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {product.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {product.description}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white">
          <h3 className="text-3xl font-bold mb-8 text-center">
            Why Customers Choose Us
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">10x</div>
              <div className="text-blue-100">Faster Workflows</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">99.9%</div>
              <div className="text-blue-100">Uptime Guarantee</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-blue-100">Expert Support</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
