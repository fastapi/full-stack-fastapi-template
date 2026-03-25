import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { marked } from "marked"
import { toast } from "sonner"
import { useSubscription } from "@/contexts/SubscriptionContext"
import { blogAPI } from "@/clients/blog"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/app/admin/blog/new")({
  component: NewPost,
})

function slugify(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
}

function NewPost() {
  const navigate = useNavigate()
  const { subscription } = useSubscription()
  const isSuperUser = subscription?.is_super_user === true

  const [title, setTitle] = useState("")
  const [slug, setSlug] = useState("")
  const [category, setCategory] = useState("GEO")
  const [excerpt, setExcerpt] = useState("")
  const [readTime, setReadTime] = useState(5)
  const [authorName, setAuthorName] = useState("Kila Team")
  const [content, setContent] = useState("")
  const [showPreview, setShowPreview] = useState(false)
  const [saving, setSaving] = useState(false)

  if (!isSuperUser) {
    navigate({ to: "/app/brands" })
    return null
  }

  const handleTitleChange = (val: string) => {
    setTitle(val)
    setSlug(slugify(val))
  }

  const save = async (publish: boolean) => {
    setSaving(true)
    try {
      const post = await blogAPI.adminCreatePost({
        slug,
        title,
        excerpt,
        content,
        category,
        read_time_minutes: readTime,
        author_name: authorName,
      })
      if (publish) {
        await blogAPI.adminTogglePublish(post.id)
      }
      toast.success(publish ? "Post created and published" : "Draft saved")
      navigate({ to: "/app/admin/blog" })
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to save")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" onClick={() => navigate({ to: "/app/admin/blog" })}>
          ← Back
        </Button>
        <h1 className="text-2xl font-bold text-slate-900">New Post</h1>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
          <input
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="Post title"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Slug</label>
            <input
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              placeholder="url-friendly-slug"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
            <select
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="GEO">GEO</option>
              <option value="SEO">SEO</option>
              <option value="STRATEGY">STRATEGY</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Read time (minutes)</label>
            <input
              type="number"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={readTime}
              onChange={(e) => setReadTime(Number(e.target.value))}
              min={1}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Author name</label>
            <input
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={authorName}
              onChange={(e) => setAuthorName(e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Excerpt</label>
          <textarea
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            value={excerpt}
            onChange={(e) => setExcerpt(e.target.value)}
            placeholder="One or two sentence summary..."
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-sm font-medium text-slate-700">Content (Markdown)</label>
            <button
              type="button"
              className="text-xs text-blue-600 hover:underline"
              onClick={() => setShowPreview((p) => !p)}
            >
              {showPreview ? "Edit" : "Preview"}
            </button>
          </div>
          {showPreview ? (
            <div
              className="border border-slate-200 rounded-lg p-4 min-h-64"
              // eslint-disable-next-line react/no-danger
              dangerouslySetInnerHTML={{ __html: marked.parse(content, { async: false }) }}
            />
          ) : (
            <textarea
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-64"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="# Heading&#10;&#10;Write your post in markdown..."
            />
          )}
        </div>

        <div className="flex gap-3 pt-2">
          <Button variant="outline" disabled={saving} onClick={() => save(false)}>
            Save Draft
          </Button>
          <Button disabled={saving} onClick={() => save(true)}>
            Save & Publish
          </Button>
        </div>
      </div>
    </div>
  )
}
