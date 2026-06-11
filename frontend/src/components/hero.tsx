import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import FileUploadZone from "@/components/FileUploadZone"
import { isLoggedIn } from "@/hooks/useAuth"

export default function Hero() {
  const [isDrag] = useState(false)
  const navigate = useNavigate()
  const { t } = useTranslation()

  const requireAuth = (action: () => void) => {
    if (!isLoggedIn()) {
      navigate({ to: "/login" })
      return
    }
    action()
  }

  const handleClick = () => {
    requireAuth(() => {
      navigate({ to: "/dashboard" })
    })
  }

  const handleFileSelect = (_file: File) => {
    requireAuth(() => {
      // navigate to dashboard where the selected file can be handled/uploaded
      navigate({ to: "/dashboard" })
    })
  }

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 via-primary/5 to-background py-16 sm:py-24 lg:py-32">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-foreground sm:text-6xl lg:text-7xl text-balance">
            {t("hero.title")}
          </h1>
          <p className="mt-6 text-xl text-muted-foreground sm:text-2xl max-w-3xl mx-auto">
            {t("hero.subtitle")}
          </p>

          <div className="mt-16 w-full">
            <FileUploadZone
              onClick={handleClick}
              onFileSelect={handleFileSelect}
              className={`cursor-pointer rounded-2xl border-2 border-dashed p-16 sm:p-20 text-center transition-all ${
                isDrag
                  ? "border-primary bg-primary/10 shadow-2xl scale-105"
                  : "border-primary/40 bg-primary/5 hover:bg-primary/8 hover:border-primary/60 shadow-lg hover:shadow-2xl"
              }`}
              title={t("hero.dragDrop")}
              description={t("hero.browse")}
              sizeHint={t("hero.sizeHint")}
            />
          </div>

          <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8">
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>{t("hero.instantConversion")}</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-foreground text-lg">
                {t("hero.instantConversion")}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t("hero.pdfsToExcel")}
              </p>
            </div>
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>{t("hero.bankGradeSecurity")}</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-foreground text-lg">
                {t("hero.bankGradeSecurity")}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t("hero.dataEncrypted")}
              </p>
            </div>
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>{t("hero.accurate")}</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-foreground text-lg">
                {t("hero.accurate")}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t("hero.preservesData")}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
