import type { BlogPostListItem } from "@/clients/blog"

const CATEGORY_STYLES: Record<string, { bar: string; badge: string; text: string }> = {
  GEO: { bar: "bg-blue-600", badge: "bg-blue-50", text: "text-blue-700" },
  SEO: { bar: "bg-amber-500", badge: "bg-amber-50", text: "text-amber-700" },
  STRATEGY: { bar: "bg-green-600", badge: "bg-green-50", text: "text-green-700" },
}

const DEFAULT_STYLE = { bar: "bg-slate-400", badge: "bg-slate-50", text: "text-slate-700" }

interface BlogCardProps {
  post: BlogPostListItem
}

export default function BlogCard({ post }: BlogCardProps) {
  const style = CATEGORY_STYLES[post.category] ?? DEFAULT_STYLE

  const formattedDate = new Date(post.published_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })

  return (
    <a
      href={`/blog/${post.slug}`}
      target="_blank"
      rel="noopener noreferrer"
      className="group block bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-md transition-shadow"
    >
      {/* Colour accent bar */}
      <div className={`h-1.5 w-full ${style.bar}`} />
      <div className="p-5">
        <div className="flex items-center gap-2 mb-3">
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${style.badge} ${style.text}`}>
            {post.category}
          </span>
          <span className="text-xs text-slate-400">
            {formattedDate} · {post.read_time_minutes} min read
          </span>
        </div>
        <h3 className="font-bold text-slate-900 text-base leading-snug mb-2 group-hover:text-blue-700 transition-colors">
          {post.title}
        </h3>
        <p className="text-sm text-slate-600 leading-relaxed line-clamp-3">{post.excerpt}</p>
      </div>
    </a>
  )
}
