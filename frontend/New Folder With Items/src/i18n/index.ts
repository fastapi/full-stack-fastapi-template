import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

import enCommon from "./locales/en/common.json"
import viCommon from "./locales/vi/common.json"

/**
 * All supported languages. To add a new language:
 * 1. Create src/i18n/locales/<code>/common.json
 * 2. Import it above and add it to `resources` below
 * 3. Add an entry to SUPPORTED_LANGUAGES
 */
export const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English", flag: "🇺🇸" },
  { code: "vi", label: "Tiếng Việt", flag: "🇻🇳" },
] as const

export type SupportedLanguageCode = (typeof SUPPORTED_LANGUAGES)[number]["code"]

const resources = {
  en: { common: enCommon },
  vi: { common: viCommon },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    defaultNS: "common",
    fallbackLng: "en",
    supportedLngs: SUPPORTED_LANGUAGES.map((l) => l.code),
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "app-language",
    },
  })

export default i18n
