import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"
import { TagsService } from "@/client"
import { TagTranslationManager } from "@/components/Admin/TagTranslationManager"
import PendingItems from "@/components/Pending/PendingItems"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export const Route = createFileRoute("/_layout/admin/tags")({
  component: AdminTags,
  head: () => ({
    meta: [
      {
        title: "Manage Tags - Admin",
      },
    ],
  }),
})

function getTagsQueryOptions() {
  return {
    queryFn: () => TagsService.listTags(),
    queryKey: ["tags"],
  }
}

function TagsContent() {
  const { data: tagsData } = useSuspenseQuery(getTagsQueryOptions())
  const tags = tagsData?.data || []

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Manage Tags</h1>
        <p className="text-muted-foreground mt-2">
          Manage tag translations for multi-language support
        </p>
      </div>

      <div className="space-y-6">
        {tags.map((tag) => (
          <Card key={tag.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {tag.name}
                    <Badge variant="outline">{tag.slug}</Badge>
                  </CardTitle>
                  <CardDescription>
                    Tag ID: {tag.id}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <TagTranslationManager tagId={tag.id} tag={tag} />
            </CardContent>
          </Card>
        ))}
      </div>

      {tags.length === 0 && (
        <Card>
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground">
              No tags found. Create tags from the races page.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function AdminTags() {
  return (
    <Suspense fallback={<PendingItems />}>
      <TagsContent />
    </Suspense>
  )
}
