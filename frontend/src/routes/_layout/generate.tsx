import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
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
  createGeneration,
  createTemplateVersion,
  extractVariables,
  getTemplate,
  listTemplates,
  listTemplateVersions,
  renderTemplate,
  type Template,
  type TemplateVariableConfig,
  type TemplateVersion,
} from "@/lib/templateMvpApi"
import { errorToMessage } from "@/lib/templateVariables"

function listToInput(value: unknown): string {
  if (!Array.isArray(value)) {
    return ""
  }
  return value.join(", ")
}

function inputToList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
}

function escapeRegExp(input: string): string {
  return input.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function generalizeOutputToTemplate(
  outputText: string,
  values: Record<string, unknown>,
): string {
  let templateContent = outputText

  const replacementEntries = Object.entries(values)
    .map(([key, value]) => [key, value] as const)
    .sort((a, b) => {
      const aLength = Array.isArray(a[1])
        ? a[1].join(", ").length
        : String(a[1] ?? "").length
      const bLength = Array.isArray(b[1])
        ? b[1].join(", ").length
        : String(b[1] ?? "").length
      return bLength - aLength
    })

  for (const [key, rawValue] of replacementEntries) {
    if (Array.isArray(rawValue)) {
      for (const item of rawValue) {
        if (!String(item).trim()) {
          continue
        }
        templateContent = templateContent.replace(
          new RegExp(escapeRegExp(String(item)), "g"),
          `{{${key}}}`,
        )
      }
      continue
    }

    if (!String(rawValue ?? "").trim()) {
      continue
    }

    templateContent = templateContent.replace(
      new RegExp(escapeRegExp(String(rawValue)), "g"),
      `{{${key}}}`,
    )
  }

  return templateContent
}

export const Route = createFileRoute("/_layout/generate")({
  component: GeneratePage,
  head: () => ({
    meta: [
      {
        title: "Generate - TemplateForge AI",
      },
    ],
  }),
})

function GeneratePage() {
  const queryClient = useQueryClient()
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("")
  const [selectedVersionId, setSelectedVersionId] = useState<string>("")
  const [inputText, setInputText] = useState("")
  const [values, setValues] = useState<Record<string, unknown>>({})
  const [missingRequired, setMissingRequired] = useState<string[]>([])
  const [outputText, setOutputText] = useState("")
  const [generalizeTemplate, setGeneralizeTemplate] = useState(true)

  const templatesQuery = useQuery({
    queryKey: ["templates", "generate"],
    queryFn: () => listTemplates(),
  })

  useEffect(() => {
    if (selectedTemplateId || !templatesQuery.data?.data.length) {
      return
    }
    setSelectedTemplateId(templatesQuery.data.data[0].id)
  }, [selectedTemplateId, templatesQuery.data])

  const templateQuery = useQuery({
    queryKey: ["template", selectedTemplateId],
    queryFn: () => getTemplate(selectedTemplateId),
    enabled: Boolean(selectedTemplateId),
  })

  const versionsQuery = useQuery({
    queryKey: ["templateVersions", selectedTemplateId],
    queryFn: () => listTemplateVersions(selectedTemplateId),
    enabled: Boolean(selectedTemplateId),
  })

  useEffect(() => {
    if (!versionsQuery.data?.data.length) {
      setSelectedVersionId("")
      return
    }
    if (
      selectedVersionId &&
      versionsQuery.data.data.some((item) => item.id === selectedVersionId)
    ) {
      return
    }
    setSelectedVersionId(versionsQuery.data.data[0].id)
  }, [selectedVersionId, versionsQuery.data])

  const currentVersion = useMemo<TemplateVersion | null>(() => {
    if (!versionsQuery.data?.data.length || !selectedVersionId) {
      return null
    }
    return (
      versionsQuery.data.data.find((item) => item.id === selectedVersionId) ||
      null
    )
  }, [selectedVersionId, versionsQuery.data])

  const currentTemplate = useMemo<Template | null>(() => {
    return templateQuery.data || null
  }, [templateQuery.data])

  const extractMutation = useMutation({
    mutationFn: extractVariables,
  })

  const renderMutation = useMutation({
    mutationFn: renderTemplate,
  })

  const saveGenerationMutation = useMutation({
    mutationFn: createGeneration,
  })

  const saveAsVersionMutation = useMutation({
    mutationFn: (payload: {
      templateId: string
      content: string
      schema: Record<string, TemplateVariableConfig>
    }) =>
      createTemplateVersion(payload.templateId, {
        content: payload.content,
        variables_schema: payload.schema,
      }),
  })

  useEffect(() => {
    if (!currentVersion) {
      setValues({})
      setMissingRequired([])
      return
    }

    const initialValues: Record<string, unknown> = {}
    for (const [variable, config] of Object.entries(
      currentVersion.variables_schema,
    )) {
      initialValues[variable] =
        config.default !== undefined && config.default !== null
          ? config.default
          : config.type === "list"
            ? []
            : ""
    }
    setValues(initialValues)
    setMissingRequired([])
    setOutputText("")
  }, [currentVersion?.id, currentVersion])

  const handleExtract = async () => {
    if (!selectedVersionId) {
      showErrorToast("Select a template version first")
      return
    }

    if (!inputText.trim()) {
      showErrorToast("Please paste your requirement text first")
      return
    }

    try {
      const result = await extractMutation.mutateAsync({
        template_version_id: selectedVersionId,
        input_text: inputText,
      })
      setValues(result.values)
      setMissingRequired(result.missing_required)
      showSuccessToast("Variables extracted")
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  const handleRender = async () => {
    if (!selectedVersionId) {
      showErrorToast("Select a template version first")
      return
    }

    try {
      const result = await renderMutation.mutateAsync({
        template_version_id: selectedVersionId,
        values,
        style: {
          tone: "professional",
          length: "medium",
        },
      })
      setOutputText(result.output_text)
      showSuccessToast("Draft generated")
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  const handleSaveGeneration = async () => {
    if (!selectedTemplateId || !selectedVersionId || !outputText.trim()) {
      showErrorToast("Generate content before saving")
      return
    }

    try {
      const title = `${currentTemplate?.name || "Generation"} ${new Date().toLocaleDateString()}`
      await saveGenerationMutation.mutateAsync({
        template_id: selectedTemplateId,
        template_version_id: selectedVersionId,
        title,
        input_text: inputText,
        extracted_values: values,
        output_text: outputText,
      })
      showSuccessToast("Generation saved")
      await queryClient.invalidateQueries({ queryKey: ["generations"] })
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  const handleSaveAsVersion = async () => {
    if (!selectedTemplateId || !currentVersion || !outputText.trim()) {
      showErrorToast("Generate and edit content before saving as a version")
      return
    }

    try {
      const versionContent = generalizeTemplate
        ? generalizeOutputToTemplate(outputText, values)
        : outputText

      await saveAsVersionMutation.mutateAsync({
        templateId: selectedTemplateId,
        content: versionContent,
        schema: currentVersion.variables_schema,
      })

      showSuccessToast("Saved as new template version")
      await queryClient.invalidateQueries({
        queryKey: ["templateVersions", selectedTemplateId],
      })
      await queryClient.invalidateQueries({
        queryKey: ["template", selectedTemplateId],
      })
      await queryClient.invalidateQueries({ queryKey: ["templates"] })
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  const updateValue = (variable: string, rawValue: string, isList: boolean) => {
    setValues((current) => ({
      ...current,
      [variable]: isList ? inputToList(rawValue) : rawValue,
    }))

    setMissingRequired((current) => current.filter((item) => item !== variable))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Generate</h1>
        <p className="text-muted-foreground">
          Select a template, extract variables, confirm values, and generate
          output.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Step A: Select Template</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <select
            className="border-input bg-background h-9 rounded-md border px-3 text-sm"
            value={selectedTemplateId}
            onChange={(event) => setSelectedTemplateId(event.target.value)}
          >
            <option value="">Select template</option>
            {templatesQuery.data?.data.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>

          <select
            className="border-input bg-background h-9 rounded-md border px-3 text-sm"
            value={selectedVersionId}
            onChange={(event) => setSelectedVersionId(event.target.value)}
            disabled={!versionsQuery.data?.data.length}
          >
            <option value="">Select version</option>
            {versionsQuery.data?.data.map((version) => (
              <option key={version.id} value={version.id}>
                v{version.version}
              </option>
            ))}
          </select>

          {templatesQuery.error ? (
            <p className="text-sm text-destructive md:col-span-2">
              {errorToMessage(templatesQuery.error)}
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step B: Input Requirement</CardTitle>
          <CardDescription>
            Paste JD, notes, or context for extraction.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <textarea
            className="border-input bg-background min-h-[180px] w-full rounded-md border p-3 text-sm"
            value={inputText}
            onChange={(event) => setInputText(event.target.value)}
          />
          <Button onClick={handleExtract} disabled={extractMutation.isPending}>
            Extract Variables
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step C: Confirm Variables</CardTitle>
          <CardDescription>
            Fill missing required fields before generating.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {currentVersion ? (
            Object.entries(currentVersion.variables_schema).map(
              ([variable, config]) => {
                const isList = config.type === "list"
                const rawValue = values[variable]

                return (
                  <div
                    key={variable}
                    className="space-y-2 rounded-md border p-3"
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-medium">{variable}</p>
                      <div className="flex items-center gap-2">
                        {missingRequired.includes(variable) ? (
                          <span className="text-xs text-destructive">
                            Missing required
                          </span>
                        ) : null}
                        {config.required ? (
                          <span className="text-xs text-muted-foreground">
                            Required
                          </span>
                        ) : null}
                      </div>
                    </div>
                    <Input
                      value={
                        isList ? listToInput(rawValue) : String(rawValue || "")
                      }
                      placeholder={isList ? "value1, value2" : "Value"}
                      onChange={(event) =>
                        updateValue(variable, event.target.value, isList)
                      }
                    />
                  </div>
                )
              },
            )
          ) : (
            <p className="text-sm text-muted-foreground">
              Select a template version to load variables.
            </p>
          )}

          <Button
            onClick={handleRender}
            disabled={renderMutation.isPending || !currentVersion}
          >
            Generate Draft
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Step D: Output</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <textarea
            className="border-input bg-background min-h-[260px] w-full rounded-md border p-3 text-sm"
            value={outputText}
            onChange={(event) => setOutputText(event.target.value)}
          />

          <div className="flex items-center gap-2 text-sm">
            <input
              id="generalize-template"
              type="checkbox"
              checked={generalizeTemplate}
              onChange={(event) => setGeneralizeTemplate(event.target.checked)}
            />
            <label htmlFor="generalize-template">
              Replace extracted values with placeholders when saving as version
            </label>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              onClick={handleSaveGeneration}
              disabled={saveGenerationMutation.isPending}
            >
              Save Generation
            </Button>
            <Button
              onClick={handleSaveAsVersion}
              disabled={saveAsVersionMutation.isPending}
            >
              Save as New Template Version
            </Button>
          </div>

          {templateQuery.error ? (
            <p className="text-sm text-destructive">
              {errorToMessage(templateQuery.error)}
            </p>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}
