import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import LanguageDetector from "i18next-browser-languagedetector"

import en from "./locales/en.json"
import vi from "./locales/vi.json"

const resources = {
  en: {
    translation: en,
  },
  vi: {
    translation: vi,
  },
}

i18n
  .use(LanguageDetector) // Detect user language
  .use(initReactI18next) // Pass i18n instance to react-i18next
  .init({
    resources,
    fallbackLng: "vi",
    supportedLngs: ["vi", "en"],
    debug: false,
    
    interpolation: {
      escapeValue: false, // React already escapes
    },
    
    detection: {
      // Order of language detection methods
      order: ["localStorage", "navigator", "htmlTag"],
      
      // Cache user language in localStorage
      caches: ["localStorage"],
      
      // localStorage key
      lookupLocalStorage: "i18nextLng",
    },
  })

export default i18n
