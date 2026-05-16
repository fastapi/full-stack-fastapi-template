import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useSearch } from "@tanstack/react-router"

/**
 * Hook to sync language from URL search params with i18next
 * This ensures the language parameter in URL takes precedence
 */
export function useLanguageSync() {
  const { i18n } = useTranslation()
  const search = useSearch({ strict: false }) as Record<string, any>

  useEffect(() => {
    const urlLang = search?.lang
    
    // If there's a lang param in URL and it's different from current language
    if (urlLang && typeof urlLang === "string" && urlLang !== i18n.language) {
      // Only change if it's a supported language
      const supportedLanguages = ["vi", "en"]
      if (supportedLanguages.includes(urlLang)) {
        i18n.changeLanguage(urlLang)
      }
    }
  }, [search?.lang, i18n])
}
