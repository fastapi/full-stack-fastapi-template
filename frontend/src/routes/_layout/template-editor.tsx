import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect, useMemo, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import useCustomToast from "@/hooks/useCustomToast"
import {
  createTemplate,
  createTemplateVersion,
  getTemplate,
  listTemplateVersions,
  type TemplateCategory,
  type TemplateLanguage,
  type TemplateVariableConfig,
  updateTemplate,
} from "@/lib/templateMvpApi"
import {
  buildPreviewValues,
  errorToMessage,
  extractTemplateVariables,
  renderTemplateText,
  syncSchemaWithContent,
} from "@/lib/templateVariables"

const CATEGORY_OPTIONS: Array<{ label: string; value: TemplateCategory }> = [
  { label: "Cover Letter", value: "cover_letter" },
  { label: "Email", value: "email" },
  { label: "Proposal", value: "proposal" },
  { label: "Other", value: "other" },
]

const LANGUAGE_OPTIONS: Array<{ label: string; value: TemplateLanguage }> = [
  { label: "English", value: "en" },
  { label: "French", value: "fr" },
  { label: "Chinese", value: "zh" },
  { label: "Other", value: "other" },
]

const DEFAULT_TEMPLATE_CONTENT = "Dear {{company}},\n\n{{body}}"

const defaultTemplateSchema = (): TemplateVariableConfig => ({
  required: false,
  type: "text",
  description: "",
  example: "",
  default: "",
})

function stringToList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
}

function listToString(value: unknown): string {
  if (!Array.isArray(value)) {
    return ""
  }
  return value.join(", ")
}

export const Route = createFileRoute("/_layout/template-editor")({
  validateSearch: (search: Record<string, unknown>) => ({
    templateId:
      typeof search.templateId === "string" && search.templateId
        ? search.templateId
        : undefined,
  }),
  component: TemplateEditorPage,
  head: () => ({
    meta: [
      {
        title: "Template Editor - FastAPI Template",
      },
    ],
  }),
})

function TemplateEditorPage() {
  const { templateId } = Route.useSearch()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const [name, setName] = useState("Untitled Template")
  const [category, setCategory] = useState<TemplateCategory>("cover_letter")
  const [language, setLanguage] = useState<TemplateLanguage>("en")
  const [tagsInput, setTagsInput] = useState("")
  const [content, setContent] = useState(DEFAULT_TEMPLATE_CONTENT)
  const [variablesSchema, setVariablesSchema] = useState<
    Record<string, TemplateVariableConfig>
  >({})
  const [preview, setPreview] = useState("")
  const [hydratedTemplateId, setHydratedTemplateId] = useState<string | null>(
    null,
  )

  const templateQuery = useQuery({
    queryKey: ["template", templateId],
    queryFn: () => getTemplate(templateId!),
    enabled: Boolean(templateId),
    refetchOnWindowFocus: false,
  })

  const versionsQuery = useQuery({
    queryKey: ["templateVersions", templateId],
    queryFn: () => listTemplateVersions(templateId!),
    enabled: Boolean(templateId),
    refetchOnWindowFocus: false,
  })

  useEffect(() => {
    if (!templateId) {
      setHydratedTemplateId(null)
      return
    }
    if (hydratedTemplateId !== null && hydratedTemplateId !== templateId) {
      setHydratedTemplateId(null)
    }
  }, [templateId, hydratedTemplateId])

  useEffect(() => {
    if (!templateQuery.data) {
      return
    }

    if (hydratedTemplateId === templateQuery.data.id) {
      return
    }

    const template = templateQuery.data
    setName(template.name)
    setCategory(template.category)
    setLanguage(template.language)
    setTagsInput(template.tags.join(", "))

    const latestContent = template.latest_version?.content || DEFAULT_TEMPLATE_CONTENT
    const latestSchema = template.latest_version?.variables_schema || {}

    setContent(latestContent)
    setVariablesSchema(syncSchemaWithContent(latestContent, latestSchema))
    setHydratedTemplateId(template.id)
  }, [templateQuery.data, hydratedTemplateId])

  useEffect(() => {
    setVariablesSchema((current) => {
      const synced = syncSchemaWithContent(content, current)
      if (JSON.stringify(synced) === JSON.stringify(current)) {
        return current
      }
      return synced
    })
  }, [content])

  const variableNames = useMemo(
    () => extractTemplateVariables(content),
    [content],
  )

  const createTemplateMutation = useMutation({
    mutationFn: createTemplate,
  })

  const updateTemplateMutation = useMutation({
    mutationFn: (payload: {
      id: string
      data: {
        name: string
        category: TemplateCategory
        language: TemplateLanguage
        tags: string[]
      }
    }) => updateTemplate(payload.id, payload.data),
  })

  const createVersionMutation = useMutation({
    mutationFn: (payload: {
      templateId: string
      content: string
      variables_schema: Record<string, TemplateVariableConfig>
    }) =>
      createTemplateVersion(payload.templateId, {
        content: payload.content,
        variables_schema: payload.variables_schema,
      }),
  })

  const parseTags = () =>
    tagsInput
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)

  const saveTemplateMetadata = async (): Promise<string> => {
    const tags = parseTags()

    if (templateId) {
      await updateTemplateMutation.mutateAsync({
        id: templateId,
        data: { name, category, language, tags },
      })
      return templateId
    }

    const created = await createTemplateMutation.mutateAsync({
      name,
      category,
      language,
      tags,
    })
    await navigate({
      to: "/template-editor",
      search: { templateId: created.id },
      replace: true,
    })
    return created.id
  }

  const handleSave = async () => {
    try {
      const currentTemplateId = await saveTemplateMetadata()

      if (!templateId) {
        await createVersionMutation.mutateAsync({
          templateId: currentTemplateId,
          content,
          variables_schema: variablesSchema,
        })
      }

      showSuccessToast("Template saved")
      await queryClient.invalidateQueries({ queryKey: ["templates"] })
      await queryClient.invalidateQueries({
        queryKey: ["template", currentTemplateId],
      })
      await queryClient.invalidateQueries({
        queryKey: ["templateVersions", currentTemplateId],
      })
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  const handleSaveNewVersion = async () => {
    try {
      const currentTemplateId = await saveTemplateMetadata()
      await createVersionMutation.mutateAsync({
        templateId: currentTemplateId,
        content,
        variables_schema: variablesSchema,
      })

      showSuccessToast("New template version saved")
      await queryClient.invalidateQueries({ queryKey: ["templates"] })
      await queryClient.invalidateQueries({
        queryKey: ["template", currentTemplateId],
      })
      await queryClient.invalidateQueries({
        queryKey: ["templateVersions", currentTemplateId],
      })
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  const handlePreview = () => {
    const values = buildPreviewValues(variablesSchema)
    setPreview(renderTemplateText(content, values))
  }

  const updateVariableConfig = (
    variableName: string,
    updater: (current: TemplateVariableConfig) => TemplateVariableConfig,
  ) => {
    setVariablesSchema((current) => {
      const base = current[variableName] || defaultTemplateSchema()
      return {
        ...current,
        [variableName]: updater(base),
      }
    })
  }

  const isSaving =
    createTemplateMutation.isPending ||
    updateTemplateMutation.isPending ||
    createVersionMutation.isPending

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Template Editor</h1>
          <p className="text-muted-foreground">
            Edit template content and keep versioned prompt assets.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={handlePreview}>
            Preview Render
          </Button>
          <Button variant="outline" onClick={handleSave} disabled={isSaving}>
            Save
          </Button>
          <Button onClick={handleSaveNewVersion} disabled={isSaving}>
            Save New Version
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Template Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2">
            <Input
              value={name}
              onChange={(event) => setName(event.target.value)}
            />

            <Input
              value={tagsInput}
              placeholder="backend, fintech"
              onChange={(event) => setTagsInput(event.target.value)}
            />

            <select
              className="border-input bg-background h-9 rounded-md border px-3 text-sm"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value as TemplateCategory)
              }
            >
              {CATEGORY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <select
              className="border-input bg-background h-9 rounded-md border px-3 text-sm"
              value={language}
              onChange={(event) =>
                setLanguage(event.target.value as TemplateLanguage)
              }
            >
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Template Content</CardTitle>
            <CardDescription>
              Use placeholders like {"{{company}}"}. Variables are synced
              automatically.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <textarea
              className="border-input bg-background min-h-[480px] w-full rounded-md border p-3 font-mono text-sm"
              value={content}
              onChange={(event) => setContent(event.target.value)}
            />
          </CardContent>
        </Card>

        <Card className="h-full">
          <CardHeader>
            <CardTitle>Variables</CardTitle>
            <CardDescription>
              {variableNames.length} variable(s) in this template
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {variableNames.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Add placeholders in the editor to configure variables.
              </p>
            ) : (
              variableNames.map((variableName) => {
                const config =
                  variablesSchema[variableName] || defaultTemplateSchema()
                const isList = config.type === "list"

                return (
                  <div
                    key={variableName}
                    className="space-y-2 rounded-lg border p-3"
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-medium">{variableName}</p>
                      <label className="flex items-center gap-2 text-xs text-muted-foreground">
                        <input
                          type="checkbox"
                          checked={config.required}
                          onChange={(event) =>
                            updateVariableConfig(variableName, (current) => ({
                              ...current,
                              required: event.target.checked,
                            }))
                          }
                        />
                        Required
                      </label>
                    </div>

                    <select
                      className="border-input bg-background h-9 w-full rounded-md border px-3 text-sm"
                      value={config.type}
                      onChange={(event) => {
                        const nextType = event.target.value as "text" | "list"
                        updateVariableConfig(variableName, (current) => ({
                          ...current,
                          type: nextType,
                          default:
                            nextType === "list"
                              ? Array.isArray(current.default)
                                ? current.default
                                : []
                              : typeof current.default === "string"
                                ? current.default
                                : "",
                          example:
                            nextType === "list"
                              ? Array.isArray(current.example)
                                ? current.example
                                : []
                              : typeof current.example === "string"
                                ? current.example
                                : "",
                        }))
                      }}
                    >
                      <option value="text">text</option>
                      <option value="list">list</option>
                    </select>

                    <Input
                      placeholder="Description"
                      value={config.description || ""}
                      onChange={(event) =>
                        updateVariableConfig(variableName, (current) => ({
                          ...current,
                          description: event.target.value,
                        }))
                      }
                    />

                    <Input
                      placeholder={isList ? "Example: a, b" : "Example"}
                      value={
                        isList
                          ? listToString(config.example)
                          : String(config.example || "")
                      }
                      onChange={(event) =>
                        updateVariableConfig(variableName, (current) => ({
                          ...current,
                          example: isList
                            ? stringToList(event.target.value)
                            : event.target.value,
                        }))
                      }
                    />

                    <Input
                      placeholder={isList ? "Default: a, b" : "Default"}
                      value={
                        isList
                          ? listToString(config.default)
                          : String(config.default || "")
                      }
                      onChange={(event) =>
                        updateVariableConfig(variableName, (current) => ({
                          ...current,
                          default: isList
                            ? stringToList(event.target.value)
                            : event.target.value,
                        }))
                      }
                    />
                  </div>
                )
              })
            )}
          </CardContent>
        </Card>
      </div>

      {templateQuery.error ? (
        <p className="text-sm text-destructive">
          {errorToMessage(templateQuery.error)}
        </p>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Version History</CardTitle>
          <CardDescription>
            {versionsQuery.data?.count || 0} version(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {versionsQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading versions...</p>
          ) : versionsQuery.data && versionsQuery.data.data.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {versionsQuery.data.data.map((version) => (
                <div
                  key={version.id}
                  className="rounded-md border px-3 py-2 text-xs"
                >
                  <p className="font-medium">v{version.version}</p>
                  <p className="text-muted-foreground">
                    {version.created_at
                      ? new Date(version.created_at).toLocaleString()
                      : "-"}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No versions yet.</p>
          )}
        </CardContent>
      </Card>

      {preview ? (
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap rounded-md border p-3 text-sm">
              {preview}
            </pre>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
