import { useEffect, useState } from "react"

export default function TestimonialSection() {
  const [current, setCurrent] = useState(0)

  const testimonials = [
    {
      quote: "This platform transformed our workflows. Game-changing!",
      author: "Sarah Chen",
      role: "CEO, TechCorp",
    },
    {
      quote: "Best investment we made. ROI in the first month.",
      author: "Michael Ross",
      role: "CTO, InnovateLabs",
    },
    {
      quote: "Exceptional support. They care about our success.",
      author: "Emily Stone",
      role: "VP Operations, DataFlow",
    },
  ]

  const logos = [
    "TechCorp",
    "InnovateLabs",
    "DataFlow",
    "CloudSync",
    "StartupHub",
    "ScaleUp",
  ]

  useEffect(() => {
    const interval = setInterval(
      () => setCurrent((prev) => (prev + 1) % testimonials.length),
      5000,
    )
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="py-20 bg-gray-50 dark:bg-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-12 text-center">
          What Our Customers Say
        </h2>

        <div className="bg-white dark:bg-gray-900 p-8 rounded-lg shadow-md mb-12 min-h-[200px]">
          <div className="text-3xl text-blue-600 mb-4">"</div>
          <p className="text-lg text-gray-700 dark:text-gray-300 mb-6 italic">
            {testimonials[current].quote}
          </p>
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold mr-4">
              {testimonials[current].author.charAt(0)}
            </div>
            <div>
              <div className="font-bold text-gray-900 dark:text-white">
                {testimonials[current].author}
              </div>
              <div className="text-gray-600 dark:text-gray-400 text-sm">
                {testimonials[current].role}
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-center text-gray-600 dark:text-gray-400 mb-6 font-semibold">
            Trusted by leading companies
          </h3>
          <div className="flex flex-wrap justify-center gap-8">
            {logos.map((logo, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-gray-900 px-6 py-4 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <span className="font-bold text-gray-700 dark:text-gray-300">
                  {logo}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
