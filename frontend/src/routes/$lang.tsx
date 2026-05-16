import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"

const SUPPORTED_LANGUAGES = ["vi", "en"]
const DEFAULT_LANGUAGE = "vi"

export const Route = createFileRoute("/$lang")({
  component: LanguageLayout,
  beforeLoad: ({ params }) => {
    // Validate language parameter
    const lang = params.lang
    if (!SUPPORTED_LANGUAGES.includes(lang)) {
      throw redirect({
        to: "/$lang",
        params: { lang: DEFAULT_LANGUAGE },
      })
    }
  },
})

function LanguageLayout() {
  const { lang } = Route.useParams()
  const { i18n } = useTranslation()

  // Sync i18n with URL language parameter
  useEffect(() => {
    if (lang && lang !== i18n.language && SUPPORTED_LANGUAGES.includes(lang)) {
      i18n.changeLanguage(lang)
    }
  }, [lang, i18n])

  return <Outlet />
}
