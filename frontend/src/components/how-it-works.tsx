import { useTranslation } from "react-i18next"

export default function HowItWorks() {
  const { t } = useTranslation()

  const steps = [
    {
      number: "1",
      title: t("howItWorks.step1.title"),
      description: t("howItWorks.step1.description"),
    },
    {
      number: "2",
      title: t("howItWorks.step2.title"),
      description: t("howItWorks.step2.description"),
    },
    {
      number: "3",
      title: t("howItWorks.step3.title"),
      description: t("howItWorks.step3.description"),
    },
  ]

  return (
    <section id="how" className="py-20 sm:py-32 bg-secondary">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            {t("howItWorks.heading")}
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            {t("howItWorks.subheading")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-16 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
              )}
              <div className="relative z-10 rounded-lg border border-border bg-background p-8">
                <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-primary text-primary-foreground font-bold text-lg mb-6 mx-auto">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold text-foreground text-center mb-3">
                  {step.title}
                </h3>
                <p className="text-center text-muted-foreground">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 rounded-lg bg-primary/5 border border-primary/20 p-8 text-center">
          <p className="text-foreground font-semibold">{t("howItWorks.cta")}</p>
        </div>
      </div>
    </section>
  )
}
