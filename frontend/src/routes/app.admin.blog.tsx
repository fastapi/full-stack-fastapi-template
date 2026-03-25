import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import { useSubscription } from "@/contexts/SubscriptionContext"
import { blogAPI } from "@/clients/blog"
import type { BlogPostAdminResponse } from "@/clients/blog"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/app/admin/blog")({
  component: AdminBlog,
})

function AdminBlog() {
  const navigate = useNavigate()
  const { subscription } = useSubscription()
  const isSuperUser = subscription?.is_super_user === true

  const [posts, setPosts] = useState<BlogPostAdminResponse[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isSuperUser) {
      navigate({ to: "/app/brands" })
      return
    }
    blogAPI
      .adminListPosts()
      .then(setPosts)
      .catch(() => toast.error("Failed to load posts"))
      .finally(() => setLoading(false))
  }, [isSuperUser, navigate])

  const handleTogglePublish = async (post: BlogPostAdminResponse) => {
    try {
      const updated = await blogAPI.adminTogglePublish(post.id)
      setPosts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))
      toast.success(updated.is_published ? "Post published" : "Post unpublished")
    } catch {
      toast.error("Failed to update post")
    }
  }

  const handleDelete = async (post: BlogPostAdminResponse) => {
    if (!window.confirm(`Delete "${post.title}"? This cannot be undone.`)) return
    try {
      await blogAPI.adminDeletePost(post.id)
      setPosts((prev) => prev.filter((p) => p.id !== post.id))
      toast.success("Post deleted")
    } catch {
      toast.error("Failed to delete post")
    }
  }

  if (!isSuperUser || loading) return null

  return (
    <div className="p-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Blog Admin</h1>
        <Button onClick={() => navigate({ to: "/app/admin/blog/new" })}>+ New Post</Button>
      </div>

      {posts.length === 0 ? (
        <p className="text-slate-500">No posts yet. Create your first one.</p>
      ) : (
        <div className="rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 uppercase text-xs tracking-wider">
              <tr>
                <th className="px-4 py-3 text-left">Title</th>
                <th className="px-4 py-3 text-left">Category</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Published</th>
                <th className="px-4 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {posts.map((post) => (
                <tr key={post.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900 max-w-xs truncate">
                    {post.title}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{post.category}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        post.is_published
                          ? "bg-green-50 text-green-700"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {post.is_published ? "Published" : "Draft"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {post.published_at
                      ? new Date(post.published_at).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigate({ to: "/app/admin/blog/$id/edit", params: { id: String(post.id) } })}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTogglePublish(post)}
                      >
                        {post.is_published ? "Unpublish" : "Publish"}
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(post)}
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
