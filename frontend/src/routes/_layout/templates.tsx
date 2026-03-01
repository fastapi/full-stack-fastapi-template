import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import {
  Archive,
  CalendarClock,
  ChevronDown,
  FilePlus2,
  Filter,
  Globe2,
  Layers3,
  PencilLine,
  RefreshCcw,
  Search,
  Sparkles,
  Tags,
} from "lucide-react"
import { useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  listTemplates,
  type TemplateCategory,
  type TemplateLanguage,
  type TemplateSummary,
} from "@/lib/templateMvpApi"
import { errorToMessage } from "@/lib/templateVariables"

const CATEGORY_OPTIONS: Array<{ label: string; value: "" | TemplateCategory }> =
  [
    { label: "All", value: "" },
    { label: "Cover Letter", value: "cover_letter" },
    { label: "Email", value: "email" },
    { label: "Proposal", value: "proposal" },
    { label: "Other", value: "other" },
  ]

const LANGUAGE_OPTIONS: Array<{ label: string; value: "" | TemplateLanguage }> =
  [
    { label: "All", value: "" },
    { label: "English", value: "en" },
    { label: "French", value: "fr" },
    { label: "Chinese", value: "zh" },
    { label: "Other", value: "other" },
  ]

const CATEGORY_LABELS: Record<TemplateCategory, string> = {
  cover_letter: "Cover Letter",
  email: "Email",
  proposal: "Proposal",
  other: "Other",
}

const LANGUAGE_LABELS: Record<TemplateLanguage, string> = {
  en: "English",
  fr: "French",
  zh: "Chinese",
  other: "Other",
}

function formatTemplateTime(value: string | null) {
  if (!value) {
    return "No activity yet"
  }

  return new Date(value).toLocaleString()
}

function selectClassName() {
  return "border-input bg-[var(--surface-input)] text-foreground h-[var(--control-height)] w-full appearance-none rounded-[var(--radius-control)] border px-3.5 pr-9 text-sm shadow-[var(--shadow-elev-1)] outline-none transition-[color,background-color,border-color,box-shadow] duration-200 focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
}

function FilterSelect({
  id,
  value,
  options,
  onChange,
}: {
  id: string
  value: string
  options: Array<{ label: string; value: string }>
  onChange: (value: string) => void
}) {
  return (
    <div className="relative">
      <select
        id={id}
        className={selectClassName()}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option.label} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown className="text-muted-foreground pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2" />
    </div>
  )
}

function TemplateCard({ template }: { template: TemplateSummary }) {
  const hasTags = template.tags.length > 0

  return (
    <div className="group bg-card/85 relative overflow-hidden rounded-[calc(var(--radius-panel)+0.2rem)] border border-border/70 p-4 shadow-[var(--shadow-elev-1)] backdrop-blur-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-[var(--shadow-elev-2)]">
      <div className="pointer-events-none absolute -top-10 -right-8 h-24 w-24 rounded-full bg-primary/8 blur-2xl" />

      <div className="relative space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0 space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-base font-semibold tracking-tight">
                {template.name}
              </h3>
              {template.is_archived ? (
                <Badge
                  variant="secondary"
                  className="bg-muted text-muted-foreground border-border"
                >
                  <Archive className="size-3" />
                  Archived
                </Badge>
              ) : (
                <Badge
                  variant="outline"
                  className="border-primary/25 bg-primary/8 text-primary"
                >
                  Active
                </Badge>
              )}
            </div>

            <div className="text-muted-foreground flex flex-wrap items-center gap-2 text-xs">
              <span className="bg-muted/70 inline-flex items-center gap-1 rounded-full px-2 py-1">
                <Layers3 className="size-3" />
                {CATEGORY_LABELS[template.category]}
              </span>
              <span className="bg-muted/70 inline-flex items-center gap-1 rounded-full px-2 py-1">
                <Globe2 className="size-3" />
                {LANGUAGE_LABELS[template.language]}
              </span>
              <span className="inline-flex items-center gap-1">
                <CalendarClock className="size-3" />
                {formatTemplateTime(template.updated_at)}
              </span>
            </div>
          </div>

          <Button asChild variant="outline" size="sm">
            <Link to="/template-editor" search={{ templateId: template.id }}>
              <PencilLine className="size-4" />
              Edit
            </Link>
          </Button>
        </div>

        <div className="grid gap-2 sm:grid-cols-3">
          <div className="bg-muted/55 rounded-[var(--radius-control)] border border-border/60 p-3">
            <p className="text-muted-foreground text-xs">Versions</p>
            <p className="mt-1 text-lg font-semibold leading-none">
              {template.versions_count}
            </p>
          </div>
          <div className="bg-muted/55 rounded-[var(--radius-control)] border border-border/60 p-3">
            <p className="text-muted-foreground text-xs">Latest</p>
            <p className="mt-1 text-lg font-semibold leading-none">
              {template.latest_version_number ?? "-"}
            </p>
          </div>
          <div className="bg-muted/55 rounded-[var(--radius-control)] border border-border/60 p-3">
            <p className="text-muted-foreground text-xs">Tags</p>
            <p className="mt-1 text-lg font-semibold leading-none">
              {template.tags.length}
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="text-muted-foreground flex items-center gap-1.5 text-xs">
            <Tags className="size-3" />
            Labels
          </div>
          {hasTags ? (
            <div className="flex flex-wrap gap-2">
              {template.tags.slice(0, 5).map((tag) => (
                <Badge
                  key={tag}
                  variant="outline"
                  className="bg-background/90 text-foreground"
                >
                  {tag}
                </Badge>
              ))}
              {template.tags.length > 5 ? (
                <Badge variant="outline" className="bg-background/90">
                  +{template.tags.length - 5} more
                </Badge>
              ) : null}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No tags yet</p>
          )}
        </div>
      </div>
    </div>
  )
}

function LoadingTemplateCards() {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {Array.from({ length: 4 }).map((_, index) => (
        <div
          key={`loading-${index}`}
          className="bg-card rounded-[calc(var(--radius-panel)+0.2rem)] border border-border/70 p-4 shadow-[var(--shadow-elev-1)]"
        >
          <div className="space-y-4 animate-pulse">
            <div className="h-4 w-2/5 rounded bg-muted" />
            <div className="h-3 w-4/5 rounded bg-muted" />
            <div className="grid gap-2 sm:grid-cols-3">
              <div className="h-20 rounded bg-muted/90" />
              <div className="h-20 rounded bg-muted/90" />
              <div className="h-20 rounded bg-muted/90" />
            </div>
            <div className="h-3 w-1/4 rounded bg-muted" />
            <div className="flex gap-2">
              <div className="h-6 w-16 rounded-full bg-muted" />
              <div className="h-6 w-20 rounded-full bg-muted" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export const Route = createFileRoute("/_layout/templates")({
  component: TemplatesPage,
  head: () => ({
    meta: [
      {
        title: "Templates - TemplateForge AI",
      },
    ],
  }),
})

function TemplatesPage() {
  const [category, setCategory] = useState<"" | TemplateCategory>("")
  const [language, setLanguage] = useState<"" | TemplateLanguage>("")
  const [search, setSearch] = useState("")

  const templatesQuery = useQuery({
    queryKey: ["templates", { category, language, search }],
    queryFn: () =>
      listTemplates({
        category: category || undefined,
        language: language || undefined,
        search: search.trim() || undefined,
      }),
  })

  const templates = templatesQuery.data?.data ?? []
  const totalTemplates = templatesQuery.data?.count ?? 0
  const archivedCount = templates.filter(
    (template) => template.is_archived,
  ).length
  const activeCount = totalTemplates - archivedCount
  const totalVersions = templates.reduce(
    (sum, template) => sum + template.versions_count,
    0,
  )
  const activeFilters = [category, language, search.trim()].filter(
    Boolean,
  ).length
  const languageCount = new Set(templates.map((template) => template.language))
    .size

  const clearFilters = () => {
    setCategory("")
    setLanguage("")
    setSearch("")
  }

  return (
    <div className="space-y-6 pb-8">
      <section className="relative overflow-hidden rounded-[calc(var(--radius-panel)+0.4rem)] border border-border/70 bg-gradient-to-br from-card via-card to-primary/5 p-5 shadow-[var(--shadow-elev-1)] md:p-6">
        <div className="pointer-events-none absolute -top-20 left-8 h-36 w-36 rounded-full bg-primary/12 blur-3xl" />
        <div className="pointer-events-none absolute right-10 bottom-0 h-28 w-28 rounded-full bg-foreground/4 blur-2xl" />

        <div className="relative flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/8 px-3 py-1 text-xs font-medium text-primary">
              <Sparkles className="size-3.5" />
              Template Workspace
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
                Templates
              </h1>
              <p className="text-muted-foreground max-w-2xl text-sm leading-6 md:text-base">
                Build reusable writing systems, organize them by language and
                category, and jump back into editing without digging through a
                plain table.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-background/75 rounded-[var(--radius-control)] border border-border/60 px-3.5 py-3 shadow-[var(--shadow-elev-1)] backdrop-blur-sm">
                <p className="text-muted-foreground text-xs">Total templates</p>
                <p className="mt-1 text-xl font-semibold leading-none">
                  {totalTemplates}
                </p>
              </div>
              <div className="bg-background/75 rounded-[var(--radius-control)] border border-border/60 px-3.5 py-3 shadow-[var(--shadow-elev-1)] backdrop-blur-sm">
                <p className="text-muted-foreground text-xs">Active</p>
                <p className="mt-1 text-xl font-semibold leading-none">
                  {activeCount}
                </p>
              </div>
              <div className="bg-background/75 rounded-[var(--radius-control)] border border-border/60 px-3.5 py-3 shadow-[var(--shadow-elev-1)] backdrop-blur-sm">
                <p className="text-muted-foreground text-xs">Versions</p>
                <p className="mt-1 text-xl font-semibold leading-none">
                  {totalVersions}
                </p>
              </div>
              <div className="bg-background/75 rounded-[var(--radius-control)] border border-border/60 px-3.5 py-3 shadow-[var(--shadow-elev-1)] backdrop-blur-sm">
                <p className="text-muted-foreground text-xs">Languages</p>
                <p className="mt-1 text-xl font-semibold leading-none">
                  {languageCount}
                </p>
              </div>
            </div>
          </div>

          <div className="flex w-full max-w-md flex-col gap-3">
            <Button asChild size="lg" className="justify-center">
              <Link to="/template-editor" search={{ templateId: undefined }}>
                <FilePlus2 className="size-4" />
                New Template
              </Link>
            </Button>

            <div className="grid gap-3 sm:grid-cols-2">
              <Button
                variant="outline"
                onClick={() => templatesQuery.refetch()}
                disabled={templatesQuery.isFetching}
                className="justify-center"
              >
                <RefreshCcw
                  className={`size-4 ${
                    templatesQuery.isFetching ? "animate-spin" : ""
                  }`}
                />
                {templatesQuery.isFetching ? "Refreshing..." : "Refresh"}
              </Button>

              <div className="bg-background/75 text-muted-foreground flex items-center justify-center gap-2 rounded-[var(--radius-control)] border border-border/60 px-3 text-sm shadow-[var(--shadow-elev-1)]">
                <Filter className="size-4" />
                {activeFilters} active filter{activeFilters === 1 ? "" : "s"}
              </div>
            </div>
          </div>
        </div>
      </section>

      <Card className="bg-card/90 backdrop-blur-sm">
        <CardHeader className="border-b border-border/60 pb-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Filter className="size-4" />
                Filters
              </CardTitle>
              <CardDescription>
                Narrow results by category, language, or template name.
              </CardDescription>
            </div>
            {activeFilters > 0 ? (
              <Badge
                variant="outline"
                className="border-primary/25 bg-primary/8 text-primary"
              >
                {activeFilters} active
              </Badge>
            ) : (
              <Badge variant="outline" className="text-muted-foreground">
                No active filters
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="pt-4">
          <div className="grid gap-3 xl:grid-cols-[1fr_1fr_1.2fr_auto]">
            <div className="space-y-1.5">
              <label
                className="text-muted-foreground text-xs font-medium"
                htmlFor="template-category-filter"
              >
                Category
              </label>
              <FilterSelect
                id="template-category-filter"
                value={category}
                options={CATEGORY_OPTIONS}
                onChange={(value) =>
                  setCategory(value as "" | TemplateCategory)
                }
              />
            </div>

            <div className="space-y-1.5">
              <label
                className="text-muted-foreground text-xs font-medium"
                htmlFor="template-language-filter"
              >
                Language
              </label>
              <FilterSelect
                id="template-language-filter"
                value={language}
                options={LANGUAGE_OPTIONS}
                onChange={(value) =>
                  setLanguage(value as "" | TemplateLanguage)
                }
              />
            </div>

            <div className="space-y-1.5">
              <label
                className="text-muted-foreground text-xs font-medium"
                htmlFor="template-search-filter"
              >
                Search
              </label>
              <div className="relative">
                <Search className="text-muted-foreground pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2" />
                <Input
                  id="template-search-filter"
                  placeholder="Search by template name"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="flex items-end gap-2">
              <Button
                variant="outline"
                onClick={() => templatesQuery.refetch()}
                disabled={templatesQuery.isFetching}
                className="flex-1 xl:flex-none"
              >
                <RefreshCcw className="size-4" />
                Refresh
              </Button>
              <Button
                variant="ghost"
                onClick={clearFilters}
                disabled={activeFilters === 0}
                className="flex-1 xl:flex-none"
              >
                Clear
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-card/90 backdrop-blur-sm">
        <CardHeader className="border-b border-border/60 pb-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Layers3 className="size-4" />
                Template Library
              </CardTitle>
              <CardDescription>
                {totalTemplates} template(s) across {Math.max(languageCount, 0)}{" "}
                language bucket{languageCount === 1 ? "" : "s"}
              </CardDescription>
            </div>
            <div className="text-muted-foreground bg-muted/60 flex items-center gap-2 rounded-full border border-border/60 px-3 py-1 text-xs">
              <Archive className="size-3.5" />
              {archivedCount} archived
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-4">
          {templatesQuery.isLoading ? (
            <LoadingTemplateCards />
          ) : templatesQuery.error ? (
            <div className="rounded-[calc(var(--radius-panel)-0.15rem)] border border-destructive/30 bg-destructive/5 p-5">
              <p className="text-destructive text-sm font-medium">
                Failed to load templates
              </p>
              <p className="text-muted-foreground mt-1 text-sm">
                {errorToMessage(templatesQuery.error)}
              </p>
              <Button
                variant="outline"
                className="mt-3"
                onClick={() => templatesQuery.refetch()}
              >
                <RefreshCcw className="size-4" />
                Retry
              </Button>
            </div>
          ) : templates.length > 0 ? (
            <div className="grid gap-4 xl:grid-cols-2">
              {templates.map((template) => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>
          ) : (
            <div className="relative overflow-hidden rounded-[calc(var(--radius-panel)+0.1rem)] border border-dashed border-border/80 bg-gradient-to-br from-muted/30 to-background p-8 text-center">
              <div className="pointer-events-none absolute inset-x-0 top-0 h-20 bg-primary/5 blur-2xl" />
              <div className="relative mx-auto max-w-md space-y-3">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-primary/20 bg-primary/8 text-primary">
                  <FilePlus2 className="size-5" />
                </div>
                <h3 className="text-lg font-semibold tracking-tight">
                  {activeFilters > 0
                    ? "No templates match these filters"
                    : "No templates yet"}
                </h3>
                <p className="text-muted-foreground text-sm leading-6">
                  {activeFilters > 0
                    ? "Try clearing filters or broadening your search to see more results."
                    : "Create your first template to start building reusable prompts and writing workflows."}
                </p>
                <div className="flex flex-wrap justify-center gap-2 pt-1">
                  <Button asChild>
                    <Link
                      to="/template-editor"
                      search={{ templateId: undefined }}
                    >
                      <FilePlus2 className="size-4" />
                      Create Template
                    </Link>
                  </Button>
                  {activeFilters > 0 ? (
                    <Button variant="outline" onClick={clearFilters}>
                      Clear Filters
                    </Button>
                  ) : null}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
