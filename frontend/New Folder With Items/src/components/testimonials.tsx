import { useTranslation } from "react-i18next"

export default function Testimonials() {
  const { t } = useTranslation()

  const testimonials = [
    {
      id: "sarah",
      name: t("testimonials.sarah.name"),
      role: t("testimonials.sarah.role"),
      content: t("testimonials.sarah.content"),
      rating: 5,
    },
    {
      id: "james",
      name: t("testimonials.james.name"),
      role: t("testimonials.james.role"),
      content: t("testimonials.james.content"),
      rating: 5,
    },
    {
      id: "emily",
      name: t("testimonials.emily.name"),
      role: t("testimonials.emily.role"),
      content: t("testimonials.emily.content"),
      rating: 5,
    },
  ]

  return (
    <section className="py-20 sm:py-32 bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            {t("testimonials.heading")}
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            {t("testimonials.subheading")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.id}
              className="rounded-lg border border-border bg-card p-8 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center gap-1 mb-4">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <span
                    key={`${testimonial.id}-${i}`}
                    className="text-yellow-400"
                  >
                    ★
                  </span>
                ))}
              </div>
              <p className="text-card-foreground mb-6 leading-relaxed">
                "{testimonial.content}"
              </p>
              <div>
                <p className="font-semibold text-card-foreground">
                  {testimonial.name}
                </p>
                <p className="text-sm text-muted-foreground">
                  {testimonial.role}
                </p>
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs font-medium text-primary">
                ✓ {t("testimonials.verified")}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
