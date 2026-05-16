import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { TagsService } from "@/client"
import type { TagPublic, TagTranslationUpdate } from "@/client"
import { TranslationEditor, type AllTranslations, type TranslationField } from "./TranslationEditor"
import useCustomToast from "@/hooks/useCustomToast"
import { Skeleton } from "@/components/ui/skeleton"

interface TagTranslationManagerProps {
  tagId: string
  tag: TagPublic
}

const TAG_TRANSLATION_FIELDS: TranslationField[] = [
  {
    name: "name",
    label: "Tag Name",
    type: "input",
    maxLength: 50,
    required: true,
  },
]

export function TagTranslationManager({ tagId, tag }: TagTranslationManagerProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Fetch current translations
  const { data: translations, isLoading } = useQuery({
    queryKey: ["tag-translations", tagId],
    queryFn: () => TagsService.getTagTranslations({ tagId }),
  })

  const updateTranslationMutation = useMutation({
    mutationFn: async ({ language, data }: { language: string; data: Partial<TagTranslationUpdate> }) => {
      return TagsService.updateTagTranslations({
        tagId,
        requestBody: {
          language,
          name: data.name,
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tag-translations", tagId] })
      queryClient.invalidateQueries({ queryKey: ["tags"] })
      showSuccessToast("Tag translations updated successfully")
    },
    onError: (error: any) => {
      const detail = error.body?.detail || "Failed to update tag translations"
      showErrorToast(detail)
    },
  })

  const handleSave = async (allTranslations: AllTranslations) => {
    // Save each language separately
    const languages = Object.keys(allTranslations)
    
    for (const language of languages) {
      const data = allTranslations[language]
      if (data && data.name) {
        await updateTranslationMutation.mutateAsync({ language, data })
      }
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  // Build initial translations
  const initialTranslations: AllTranslations = (translations as AllTranslations) || {}

  // Ensure default language has values from the tag object
  if (!initialTranslations["vi"]) {
    initialTranslations["vi"] = {
      name: tag.name,
    }
  }

  return (
    <TranslationEditor
      fields={TAG_TRANSLATION_FIELDS}
      currentTranslations={initialTranslations}
      defaultLanguage="vi"
      onSave={handleSave}
      isSaving={updateTranslationMutation.isPending}
      title="Tag Translations"
      description="Manage translations for this tag"
    />
  )
}
