import { createFileRoute, useParams } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import BlogLayout from "@/components/blog/BlogLayout"
import BlogPostPage from "@/components/blog/BlogPostPage"
import { blogAPI } from "@/clients/blog"
import type { BlogPostPublicResponse } from "@/clients/blog"

export const Route = createFileRoute("/blog/$slug")({
  component: BlogPost,
})

function BlogPost() {
  const { slug } = useParams({ from: "/blog/$slug" })
  const [post, setPost] = useState<BlogPostPublicResponse | null>(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    blogAPI
      .getPost(slug)
      .then(setPost)
      .catch(() => setNotFound(true))
  }, [slug])

  if (notFound) {
    return (
      <BlogLayout>
        <div className="max-w-2xl mx-auto px-4 py-24 text-center">
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Post not found</h1>
          <a href="/blog" className="text-blue-600 hover:underline">← Back to Blog</a>
        </div>
      </BlogLayout>
    )
  }

  if (!post) {
    return (
      <BlogLayout>
        <div className="max-w-2xl mx-auto px-4 py-24 text-center text-slate-400">Loading...</div>
      </BlogLayout>
    )
  }

  return (
    <BlogLayout>
      <BlogPostPage post={post} />
    </BlogLayout>
  )
}
