import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { useMemo, useState } from "react"

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

  const queryKey = useMemo(
    () => ["templates", { category, language, search }],
    [category, language, search],
  )

  const templatesQuery = useQuery({
    queryKey,
    queryFn: () =>
      listTemplates({
        category: category || undefined,
        language: language || undefined,
        search: search.trim() || undefined,
      }),
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Templates</h1>
          <p className="text-muted-foreground">
            Create, filter, and manage your writing templates.
          </p>
        </div>
        <Button asChild>
          <Link to="/template-editor" search={{ templateId: undefined }}>
            New Template
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Filter by category, language, or name.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-4">
            <select
              className="border-input bg-background h-9 rounded-md border px-3 text-sm"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value as "" | TemplateCategory)
              }
            >
              {CATEGORY_OPTIONS.map((option) => (
                <option key={option.label} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <select
              className="border-input bg-background h-9 rounded-md border px-3 text-sm"
              value={language}
              onChange={(event) =>
                setLanguage(event.target.value as "" | TemplateLanguage)
              }
            >
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option.label} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <Input
              placeholder="Search by name"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />

            <Button
              variant="outline"
              onClick={() => templatesQuery.refetch()}
              disabled={templatesQuery.isFetching}
            >
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Template List</CardTitle>
          <CardDescription>
            {templatesQuery.data?.count || 0} template(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {templatesQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">
              Loading templates...
            </p>
          ) : templatesQuery.error ? (
            <p className="text-sm text-destructive">
              {errorToMessage(templatesQuery.error)}
            </p>
          ) : templatesQuery.data && templatesQuery.data.data.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground">
                    <th className="py-2">Name</th>
                    <th className="py-2">Category</th>
                    <th className="py-2">Language</th>
                    <th className="py-2">Updated</th>
                    <th className="py-2">Versions</th>
                    <th className="py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {templatesQuery.data.data.map((template) => (
                    <tr key={template.id} className="border-t">
                      <td className="py-3 pr-4 font-medium">{template.name}</td>
                      <td className="py-3 pr-4">{template.category}</td>
                      <td className="py-3 pr-4">{template.language}</td>
                      <td className="py-3 pr-4">
                        {template.updated_at
                          ? new Date(template.updated_at).toLocaleString()
                          : "-"}
                      </td>
                      <td className="py-3 pr-4">{template.versions_count}</td>
                      <td className="py-3">
                        <Button asChild size="sm" variant="outline">
                          <Link
                            to="/template-editor"
                            search={{ templateId: template.id }}
                          >
                            Edit
                          </Link>
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No templates yet. Create your first template.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
