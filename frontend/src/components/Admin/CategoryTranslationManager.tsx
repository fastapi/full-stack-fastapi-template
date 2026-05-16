import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { RaceCategoriesService } from "@/client"
import type { RaceCategoryPublic, CategoryTranslationUpdate } from "@/client"
import { TranslationEditor, type AllTranslations, type TranslationField } from "./TranslationEditor"
import useCustomToast from "@/hooks/useCustomToast"
import { Skeleton } from "@/components/ui/skeleton"

interface CategoryTranslationManagerProps {
  categoryId: string
  category: RaceCategoryPublic
}

const CATEGORY_TRANSLATION_FIELDS: TranslationField[] = [
  {
    name: "name",
    label: "Category Name",
    type: "input",
    maxLength: 100,
    required: true,
  },
  {
    name: "description",
    label: "Description",
    type: "textarea",
  },
]

export function CategoryTranslationManager({ categoryId, category }: CategoryTranslationManagerProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Fetch current translations
  const { data: translations, isLoading } = useQuery({
    queryKey: ["category-translations", categoryId],
    queryFn: () => RaceCategoriesService.getCategoryTranslations({ categoryId }),
  })

  const updateTranslationMutation = useMutation({
    mutationFn: async ({ language, data }: { language: string; data: Partial<CategoryTranslationUpdate> }) => {
      return RaceCategoriesService.updateCategoryTranslations({
        categoryId,
        requestBody: {
          language,
          name: data.name,
          description: data.description,
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["category-translations", categoryId] })
      queryClient.invalidateQueries({ queryKey: ["race-categories"] })
      showSuccessToast("Category translations updated successfully")
    },
    onError: (error: any) => {
      const detail = error.body?.detail || "Failed to update category translations"
      showErrorToast(detail)
    },
  })

  const handleSave = async (allTranslations: AllTranslations) => {
    // Save each language separately
    const languages = Object.keys(allTranslations)
    
    for (const language of languages) {
      const data = allTranslations[language]
      if (data && (data.name || data.description)) {
        await updateTranslationMutation.mutateAsync({ language, data })
      }
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  // Build initial translations
  const initialTranslations: AllTranslations = (translations as AllTranslations) || {}

  // Ensure default language has values from the category object
  if (!initialTranslations["vi"]) {
    initialTranslations["vi"] = {
      name: category.name,
      description: category.description || "",
    }
  }

  return (
    <TranslationEditor
      fields={CATEGORY_TRANSLATION_FIELDS}
      currentTranslations={initialTranslations}
      defaultLanguage="vi"
      onSave={handleSave}
      isSaving={updateTranslationMutation.isPending}
      title="Category Translations"
      description="Manage translations for this race category"
    />
  )
}
