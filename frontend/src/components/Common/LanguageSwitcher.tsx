import { Check, Globe } from "lucide-react"
import { useTranslation } from "react-i18next"
import { useParams } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const languages = [
  { code: "vi", name: "Vietnamese", nativeName: "Tiếng Việt" },
  { code: "en", name: "English", nativeName: "English" },
]

export function LanguageSwitcher() {
  const { i18n } = useTranslation()
  const params = useParams({ strict: false }) as Record<string, any>

  const changeLanguage = (languageCode: string) => {
    i18n.changeLanguage(languageCode)
    
    // Navigate to the same route with different language
    const currentPath = window.location.pathname
    
    // Extract current language from URL path (more reliable than params in some cases)
    const pathMatch = currentPath.match(/^\/([a-z]{2})(\/|$)/)
    const currentLang = pathMatch ? pathMatch[1] : (params?.lang || "vi")
    
    // More robust path replacement
    let newPath: string
    if (currentPath === `/${currentLang}` || currentPath === `/${currentLang}/`) {
      // Homepage or base language route
      newPath = `/${languageCode}/`
    } else if (currentPath.startsWith(`/${currentLang}/`)) {
      // Other pages under language prefix
      newPath = currentPath.replace(`/${currentLang}/`, `/${languageCode}/`)
    } else if (currentPath.startsWith(`/${currentLang}`)) {
      // Handle case without trailing slash
      newPath = currentPath.replace(`/${currentLang}`, `/${languageCode}`)
    } else {
      // Fallback - just navigate to the language homepage
      newPath = `/${languageCode}/`
    }
    
    // Use window.location.href to avoid nested anchor issues
    window.location.href = newPath
  }

  const currentLanguage = languages.find((lang) => lang.code === i18n.language) || languages[0]

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="gap-2">
          <Globe className="h-5 w-5" />
          <span className="sr-only">Select language</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {languages.map((language) => (
          <DropdownMenuItem
            key={language.code}
            onClick={() => changeLanguage(language.code)}
            className="flex items-center justify-between cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <span className="text-sm font-medium">{language.nativeName}</span>
              <span className="text-xs text-muted-foreground">({language.name})</span>
            </span>
            {currentLanguage.code === language.code && (
              <Check className="h-4 w-4 text-primary ml-2" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
