"use client"

import * as Accordion from "@radix-ui/react-accordion"
import { useTranslation } from "react-i18next"

export default function FAQ() {
  const { t } = useTranslation()

  const faqs = [
    {
      id: "whatIs",
      question: t("faq.whatIs.question"),
      answer: t("faq.whatIs.answer"),
    },
    {
      id: "isSafe",
      question: t("faq.isSafe.question"),
      answer: t("faq.isSafe.answer"),
    },
    {
      id: "pricing",
      question: t("faq.pricing.question"),
      answer: t("faq.pricing.answer"),
    },
    {
      id: "fileTypes",
      question: t("faq.fileTypes.question"),
      answer: t("faq.fileTypes.answer"),
    },
    {
      id: "problems",
      question: t("faq.problems.question"),
      answer: t("faq.problems.answer"),
    },
  ]

  return (
    <section id="faq" className="py-20 sm:py-32 bg-secondary">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            {t("faq.heading")}
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            {t("faq.subheading")}
          </p>
        </div>

        <Accordion.Root type="single" collapsible className="space-y-4">
          {faqs.map((faq, index) => (
            <Accordion.Item
              key={faq.id}
              value={`item-${index}`}
              className="rounded-lg border border-border bg-background overflow-hidden"
            >
              <Accordion.Header>
                <Accordion.Trigger className="flex w-full items-center justify-between px-6 py-4 text-left font-semibold text-foreground hover:text-primary transition-colors [&[data-state=open]>svg]:rotate-180">
                  <span>{faq.question}</span>
                  <svg
                    className="h-5 w-5 transition-transform duration-200"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <title>Toggle answer</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </Accordion.Trigger>
              </Accordion.Header>
              <Accordion.Content className="px-6 pb-4 pt-0 text-muted-foreground leading-relaxed">
                {faq.answer}
              </Accordion.Content>
            </Accordion.Item>
          ))}
        </Accordion.Root>
      </div>
    </section>
  )
}
