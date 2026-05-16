import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Globe, Save } from "lucide-react"

export interface TranslationField {
  name: string
  label: string
  type: "input" | "textarea"
  maxLength?: number
  required?: boolean
}

export interface LanguageTranslations {
  [key: string]: string
}

export interface AllTranslations {
  [language: string]: LanguageTranslations
}

interface TranslationEditorProps {
  fields: TranslationField[]
  currentTranslations: AllTranslations
  defaultLanguage?: string
  supportedLanguages?: Array<{ code: string; name: string; nativeName: string }>
  onSave: (translations: AllTranslations) => Promise<void>
  isSaving?: boolean
  title?: string
  description?: string
}

const DEFAULT_LANGUAGES = [
  { code: "vi", name: "Vietnamese", nativeName: "Tiếng Việt" },
  { code: "en", name: "English", nativeName: "English" },
]

export function TranslationEditor({
  fields,
  currentTranslations,
  defaultLanguage = "vi",
  supportedLanguages = DEFAULT_LANGUAGES,
  onSave,
  isSaving = false,
  title = "Manage Translations",
  description = "Edit content in multiple languages",
}: TranslationEditorProps) {
  const { t } = useTranslation()
  const [translations, setTranslations] = useState<AllTranslations>(
    currentTranslations || {}
  )
  const [activeLanguage, setActiveLanguage] = useState<string>(defaultLanguage)

  const handleFieldChange = (
    language: string,
    fieldName: string,
    value: string
  ) => {
    setTranslations((prev) => ({
      ...prev,
      [language]: {
        ...(prev[language] || {}),
        [fieldName]: value,
      },
    }))
  }

  const handleSave = async () => {
    await onSave(translations)
  }

  const getFieldValue = (language: string, fieldName: string): string => {
    return translations[language]?.[fieldName] || ""
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              {title}
            </CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Button onClick={handleSave} disabled={isSaving}>
            <Save className="mr-2 h-4 w-4" />
            {isSaving ? t("common.saving") : t("common.save")}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeLanguage} onValueChange={setActiveLanguage}>
          <TabsList className="grid w-full grid-cols-2">
            {supportedLanguages.map((lang) => (
              <TabsTrigger key={lang.code} value={lang.code}>
                {lang.nativeName}
              </TabsTrigger>
            ))}
          </TabsList>
          {supportedLanguages.map((lang) => (
            <TabsContent key={lang.code} value={lang.code} className="space-y-4">
              <div className="rounded-md bg-muted/50 p-3 text-sm">
                {lang.code === defaultLanguage ? (
                  <p className="text-muted-foreground">
                    <strong>Default language:</strong> This is the primary language for this content.
                  </p>
                ) : (
                  <p className="text-muted-foreground">
                    <strong>Translation to {lang.name}:</strong> Translate the content from the default language.
                  </p>
                )}
              </div>
              {fields.map((field) => (
                <div key={field.name} className="space-y-2">
                  <Label htmlFor={`${lang.code}-${field.name}`}>
                    {field.label}
                    {field.required && <span className="text-destructive ml-1">*</span>}
                  </Label>
                  {field.type === "input" ? (
                    <Input
                      id={`${lang.code}-${field.name}`}
                      value={getFieldValue(lang.code, field.name)}
                      onChange={(e) =>
                        handleFieldChange(lang.code, field.name, e.target.value)
                      }
                      maxLength={field.maxLength}
                      placeholder={`Enter ${field.label.toLowerCase()} in ${lang.name}`}
                    />
                  ) : (
                    <Textarea
                      id={`${lang.code}-${field.name}`}
                      value={getFieldValue(lang.code, field.name)}
                      onChange={(e) =>
                        handleFieldChange(lang.code, field.name, e.target.value)
                      }
                      maxLength={field.maxLength}
                      placeholder={`Enter ${field.label.toLowerCase()} in ${lang.name}`}
                      rows={6}
                    />
                  )}
                  {field.maxLength && (
                    <p className="text-xs text-muted-foreground text-right">
                      {getFieldValue(lang.code, field.name).length} / {field.maxLength}
                    </p>
                  )}
                </div>
              ))}
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  )
}
