export type TemplateCategory = "cover_letter" | "email" | "proposal" | "other"
export type TemplateLanguage = "fr" | "en" | "zh" | "other"
export type TemplateVariableType = "text" | "list"

export interface TemplateVariableConfig {
  required: boolean
  type: TemplateVariableType
  description: string
  example: unknown
  default: unknown
}

export interface TemplateVersion {
  id: string
  template_id: string
  version: number
  content: string
  variables_schema: Record<string, TemplateVariableConfig>
  created_at: string | null
  created_by: string
}

export interface TemplateSummary {
  id: string
  user_id: string
  name: string
  category: TemplateCategory
  language: TemplateLanguage
  tags: string[]
  is_archived: boolean
  created_at: string | null
  updated_at: string | null
  versions_count: number
  latest_version_number: number | null
}

export interface Template {
  id: string
  user_id: string
  name: string
  category: TemplateCategory
  language: TemplateLanguage
  tags: string[]
  is_archived: boolean
  created_at: string | null
  updated_at: string | null
  versions_count: number
  latest_version: TemplateVersion | null
}

export interface TemplatesResponse {
  data: TemplateSummary[]
  count: number
}

export interface TemplateVersionsResponse {
  data: TemplateVersion[]
  count: number
}

export interface ExtractVariablesResponse {
  values: Record<string, unknown>
  missing_required: string[]
  confidence: Record<string, number>
  notes: Record<string, string>
}

export interface Generation {
  id: string
  user_id: string
  template_id: string
  template_version_id: string
  title: string
  input_text: string
  extracted_values: Record<string, unknown>
  output_text: string
  created_at: string | null
  updated_at: string | null
}

export interface GenerationsResponse {
  data: Generation[]
  count: number
}

export interface RecentTemplate {
  template_id: string
  template_name: string
  category: TemplateCategory
  language: TemplateLanguage
  last_used_at: string
  usage_count: number
}

export interface RecentTemplatesResponse {
  data: RecentTemplate[]
  count: number
}

export interface CreateTemplatePayload {
  name: string
  category: TemplateCategory
  language: TemplateLanguage
  tags: string[]
}

export interface UpdateTemplatePayload {
  name?: string
  category?: TemplateCategory
  language?: TemplateLanguage
  tags?: string[]
  is_archived?: boolean
}

export interface CreateTemplateVersionPayload {
  content: string
  variables_schema: Record<string, TemplateVariableConfig>
}

export interface ExtractVariablesPayload {
  template_version_id: string
  input_text: string
  profile_context?: Record<string, unknown>
}

export interface RenderTemplatePayload {
  template_version_id: string
  values: Record<string, unknown>
  style?: {
    tone?: string
    length?: string
  }
}

export interface CreateGenerationPayload {
  template_id: string
  template_version_id: string
  title: string
  input_text: string
  extracted_values: Record<string, unknown>
  output_text: string
}

export interface UpdateGenerationPayload {
  title?: string
  extracted_values?: Record<string, unknown>
  output_text?: string
}

const API_BASE = `${import.meta.env.VITE_API_URL.replace(/\/$/, "")}/api/v1`

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = localStorage.getItem("access_token")
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    let detail = "Request failed"
    try {
      const body = (await response.json()) as { detail?: unknown }
      if (typeof body.detail === "string") {
        detail = body.detail
      }
    } catch {
      // Ignore JSON parse errors and keep fallback message.
    }
    throw new Error(detail)
  }

  return (await response.json()) as T
}

export async function listTemplates(
  params: {
    category?: TemplateCategory
    language?: TemplateLanguage
    search?: string
  } = {},
): Promise<TemplatesResponse> {
  const query = new URLSearchParams()
  if (params.category) {
    query.set("category", params.category)
  }
  if (params.language) {
    query.set("language", params.language)
  }
  if (params.search) {
    query.set("search", params.search)
  }

  const suffix = query.toString() ? `/?${query.toString()}` : "/"
  return apiRequest<TemplatesResponse>(`/templates${suffix}`)
}

export async function createTemplate(
  payload: CreateTemplatePayload,
): Promise<Template> {
  return apiRequest<Template>("/templates/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}

export async function getTemplate(templateId: string): Promise<Template> {
  return apiRequest<Template>(`/templates/${templateId}`)
}

export async function updateTemplate(
  templateId: string,
  payload: UpdateTemplatePayload,
): Promise<Template> {
  return apiRequest<Template>(`/templates/${templateId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}

export async function listTemplateVersions(
  templateId: string,
): Promise<TemplateVersionsResponse> {
  return apiRequest<TemplateVersionsResponse>(
    `/templates/${templateId}/versions`,
  )
}

export async function createTemplateVersion(
  templateId: string,
  payload: CreateTemplateVersionPayload,
): Promise<TemplateVersion> {
  return apiRequest<TemplateVersion>(`/templates/${templateId}/versions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}

export async function extractVariables(
  payload: ExtractVariablesPayload,
): Promise<ExtractVariablesResponse> {
  return apiRequest<ExtractVariablesResponse>("/generate/extract", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}

export async function renderTemplate(
  payload: RenderTemplatePayload,
): Promise<{ output_text: string }> {
  return apiRequest<{ output_text: string }>("/generate/render", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}

export async function createGeneration(
  payload: CreateGenerationPayload,
): Promise<Generation> {
  return apiRequest<Generation>("/generations/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}

export async function listGenerations(): Promise<GenerationsResponse> {
  return apiRequest<GenerationsResponse>("/generations/")
}

export async function listRecentTemplates(
  limit = 5,
): Promise<RecentTemplatesResponse> {
  const query = new URLSearchParams()
  query.set("limit", String(limit))
  return apiRequest<RecentTemplatesResponse>(
    `/dashboard/recent-templates?${query.toString()}`,
  )
}

export async function getGeneration(generationId: string): Promise<Generation> {
  return apiRequest<Generation>(`/generations/${generationId}`)
}

export async function updateGeneration(
  generationId: string,
  payload: UpdateGenerationPayload,
): Promise<Generation> {
  return apiRequest<Generation>(`/generations/${generationId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
}
