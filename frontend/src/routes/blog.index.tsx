import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import BlogLayout from "@/components/blog/BlogLayout"
import BlogListPage from "@/components/blog/BlogListPage"
import { blogAPI } from "@/clients/blog"
import type { BlogPostListItem } from "@/clients/blog"

export const Route = createFileRoute("/blog/")({
  component: BlogIndex,
})

function BlogIndex() {
  const [posts, setPosts] = useState<BlogPostListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    blogAPI
      .getPosts()
      .then(setPosts)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <BlogLayout>
        <div className="max-w-5xl mx-auto px-4 py-24 text-center text-slate-400">Loading...</div>
      </BlogLayout>
    )
  }

  return (
    <BlogLayout>
      <BlogListPage posts={posts} />
    </BlogLayout>
  )
}
