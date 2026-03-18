import { ChevronDown, ChevronUp } from "lucide-react"
import { useState } from "react"

interface FAQItem {
  question: string
  answer: string
}

const faqs: FAQItem[] = [
  {
    question: "What is GEO and why does it matter?",
    answer:
      "GEO (Generative Engine Optimization) is the practice of optimizing your brand's visibility in AI-powered search results like Google Gemini, ChatGPT, and Claude. As more buyers use AI to research products and services, appearing in these responses directly impacts your bottom line.",
  },
  {
    question: "How does Kila track AI visibility?",
    answer:
      "Kila uses advanced AI scraping to monitor how your brand appears in AI search results across multiple platforms. We track visibility share, ranking positions, citations, and sentiment to give you a complete picture of your AI presence.",
  },
  {
    question: "What data sources does Kila monitor?",
    answer:
      "Kila monitors major AI platforms including Google Gemini, OpenAI ChatGPT, Anthropic Claude, Microsoft Copilot, and other leading AI assistants. We analyze both organic results and sponsored content to ensure comprehensive coverage.",
  },
  {
    question: "How often is data updated?",
    answer:
      "Kila provides daily tracking for all monitored brands. You can view historical data going back to when you started monitoring, with the ability to compare performance across different time periods.",
  },
  {
    question: "Can I track competitors?",
    answer:
      "Yes! Kila's competitive analysis features allow you to compare your brand against up to 10 competitors. Track their visibility, analyze gap trends, and receive alerts when competitors make moves in your market.",
  },
  {
    question: "Is there a free trial?",
    answer:
      "Yes, we offer a 14-day free trial with full access to all features. No credit card required. You can add up to 3 brands and explore the complete platform before deciding to upgrade.",
  },
]

function FAQAccordionItem({
  item,
  isOpen,
  onToggle,
}: {
  item: FAQItem
  isOpen: boolean
  onToggle: () => void
}) {
  return (
    <div className="border border-slate-200 rounded-2xl overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between p-6 text-left hover:bg-slate-50 transition-colors"
      >
        <span className="font-display font-semibold text-lg text-slate-900 pr-4">
          {item.question}
        </span>
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
        >
          {isOpen ? (
            <ChevronUp className="h-4 w-4 text-slate-600" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-600" />
          )}
        </div>
      </button>
      <div
        className={`overflow-hidden transition-all duration-300 ${isOpen ? "max-h-96" : "max-h-0"}`}
      >
        <div className="px-6 pb-6">
          <p className="font-body text-base text-slate-600 leading-relaxed">
            {item.answer}
          </p>
        </div>
      </div>
    </div>
  )
}

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const handleToggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section className="relative py-24 bg-slate-50">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/4 left-[-10%] w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-[-10%] w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-blue-600 mb-4">
            FAQ
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900">
            Frequently Asked Questions
          </h2>
          <p className="font-body text-base text-slate-600 mt-4">
            Everything you need to know about Kila
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <FAQAccordionItem
              key={idx}
              item={faq}
              isOpen={openIndex === idx}
              onToggle={() => handleToggle(idx)}
            />
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-slate-600 font-body">
            Still have questions?{" "}
            <button
              type="button"
              className="text-blue-600 font-semibold hover:underline"
            >
              Contact our team
            </button>
          </p>
        </div>
      </div>
    </section>
  )
}
