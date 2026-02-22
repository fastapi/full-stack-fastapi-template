import type {
  TemplateVariableConfig,
  TemplateVariableType,
} from "@/lib/templateMvpApi"

const VARIABLE_REGEX = /{{\s*([a-zA-Z0-9_]+)\s*}}/g

export function extractTemplateVariables(content: string): string[] {
  const seen = new Set<string>()
  const variables: string[] = []

  const matches = content.matchAll(VARIABLE_REGEX)
  for (const match of matches) {
    const variable = match[1]
    if (!seen.has(variable)) {
      seen.add(variable)
      variables.push(variable)
    }
  }

  return variables
}

const defaultConfig = (
  type: TemplateVariableType = "text",
): TemplateVariableConfig => ({
  required: false,
  type,
  description: "",
  example: type === "list" ? [] : "",
  default: type === "list" ? [] : "",
})

export function syncSchemaWithContent(
  content: string,
  schema: Record<string, TemplateVariableConfig>,
): Record<string, TemplateVariableConfig> {
  const variables = extractTemplateVariables(content)
  const next: Record<string, TemplateVariableConfig> = {}

  for (const variable of variables) {
    next[variable] = schema[variable] || defaultConfig()
  }

  return next
}

function valueToText(value: unknown): string {
  if (Array.isArray(value)) {
    return value
      .map((item) => String(item).trim())
      .filter(Boolean)
      .join(", ")
  }
  if (value === null || value === undefined) {
    return ""
  }
  return String(value)
}

export function renderTemplateText(
  content: string,
  values: Record<string, unknown>,
): string {
  return content.replace(VARIABLE_REGEX, (_, variable: string) => {
    return valueToText(values[variable])
  })
}

export function buildPreviewValues(
  schema: Record<string, TemplateVariableConfig>,
): Record<string, unknown> {
  const values: Record<string, unknown> = {}

  for (const [name, config] of Object.entries(schema)) {
    if (
      config.default !== null &&
      config.default !== undefined &&
      config.default !== ""
    ) {
      values[name] = config.default
      continue
    }
    if (
      config.example !== null &&
      config.example !== undefined &&
      config.example !== ""
    ) {
      values[name] = config.example
      continue
    }
    values[name] = config.type === "list" ? [] : `{{${name}}}`
  }

  return values
}

export function errorToMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  return "Request failed"
}
