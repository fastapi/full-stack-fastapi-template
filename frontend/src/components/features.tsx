import { useTranslation } from "react-i18next"

export default function Features() {
  const { t } = useTranslation()

  const features = [
    {
      icon: "📄",
      title: t("features.multipleFileTypes.title"),
      description: t("features.multipleFileTypes.description"),
    },
    {
      icon: "🔒",
      title: t("features.security.title"),
      description: t("features.security.description"),
    },
    {
      icon: "⚡",
      title: t("features.instantConversion.title"),
      description: t("features.instantConversion.description"),
    },
    {
      icon: "✅",
      title: t("features.accurateExtraction.title"),
      description: t("features.accurateExtraction.description"),
    },
    {
      icon: "📊",
      title: t("features.readyForAnalysis.title"),
      description: t("features.readyForAnalysis.description"),
    },
    {
      icon: "🚀",
      title: t("features.zeroSetup.title"),
      description: t("features.zeroSetup.description"),
    },
  ]

  return (
    <section id="features" className="py-20 sm:py-32 bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            {t("features.heading")}
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            {t("features.subheading")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={`${feature.title}-${index}`}
              className="rounded-lg border border-border bg-card p-8 hover:border-primary/50 hover:shadow-lg transition-all"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-card-foreground mb-2">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
