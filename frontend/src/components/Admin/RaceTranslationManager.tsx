import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { RacesService } from "@/client"
import type { RacePublic, RaceTranslationUpdate } from "@/client"
import { TranslationEditor, type AllTranslations, type TranslationField } from "./TranslationEditor"
import useCustomToast from "@/hooks/useCustomToast"
import { Skeleton } from "@/components/ui/skeleton"

interface RaceTranslationManagerProps {
  raceId: string
  race: RacePublic
}

const RACE_TRANSLATION_FIELDS: TranslationField[] = [
  {
    name: "name",
    label: "Race Name",
    type: "input",
    maxLength: 255,
    required: true,
  },
  {
    name: "description",
    label: "Description",
    type: "textarea",
    maxLength: 2000,
  },
  {
    name: "location",
    label: "Location",
    type: "input",
    maxLength: 255,
  },
]

export function RaceTranslationManager({ raceId, race }: RaceTranslationManagerProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Fetch current translations
  const { data: translations, isLoading } = useQuery({
    queryKey: ["race-translations", raceId],
    queryFn: () => RacesService.getRaceTranslations({ raceId }),
  })

  const updateTranslationMutation = useMutation({
    mutationFn: async ({ language, data }: { language: string; data: Partial<RaceTranslationUpdate> }) => {
      return RacesService.updateRaceTranslations({
        raceId,
        requestBody: {
          language,
          name: data.name,
          description: data.description,
          location: data.location,
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["race-translations", raceId] })
      queryClient.invalidateQueries({ queryKey: ["races", raceId] })
      showSuccessToast("Translations updated successfully")
    },
    onError: (error: any) => {
      const detail = error.body?.detail || "Failed to update translations"
      showErrorToast(detail)
    },
  })

  const handleSave = async (allTranslations: AllTranslations) => {
    // Save each language separately
    const languages = Object.keys(allTranslations)
    
    for (const language of languages) {
      const data = allTranslations[language]
      if (data && (data.name || data.description || data.location)) {
        await updateTranslationMutation.mutateAsync({ language, data })
      }
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  // Build initial translations from race data and fetched translations
  const initialTranslations: AllTranslations = (translations as AllTranslations) || {}

  // Ensure default language has values from the race object
  if (!initialTranslations[race.default_language || "vi"]) {
    initialTranslations[race.default_language || "vi"] = {
      name: race.name,
      description: race.description || "",
      location: race.location || "",
    }
  }

  return (
    <TranslationEditor
      fields={RACE_TRANSLATION_FIELDS}
      currentTranslations={initialTranslations}
      defaultLanguage={race.default_language || "vi"}
      onSave={handleSave}
      isSaving={updateTranslationMutation.isPending}
      title="Race Translations"
      description="Manage translations for this race in multiple languages"
    />
  )
}
