import BlogCard from "./BlogCard"
import type { BlogPostListItem } from "@/clients/blog"

interface BlogListPageProps {
  posts: BlogPostListItem[]
}

export default function BlogListPage({ posts }: BlogListPageProps) {
  if (posts.length === 0) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-24 text-center text-slate-500">
        No posts yet — check back soon.
      </div>
    )
  }

  const [hero, ...rest] = posts

  const heroDate = new Date(hero.published_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">Blog</h1>

      {/* Hero post */}
      <a
        href={`/blog/${hero.slug}`}
        target="_blank"
        rel="noopener noreferrer"
        className="group block rounded-2xl overflow-hidden bg-gradient-to-br from-[#1e3a5f] to-[#1e40af] p-8 mb-10 hover:opacity-95 transition-opacity"
      >
        <div className="inline-block text-xs font-semibold text-blue-300 uppercase tracking-widest mb-3">
          {hero.category} · {hero.read_time_minutes} min read
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-white leading-tight mb-3 group-hover:underline decoration-white/40 underline-offset-4">
          {hero.title}
        </h2>
        <p className="text-blue-100 text-sm leading-relaxed mb-4 max-w-2xl">{hero.excerpt}</p>
        <div className="flex items-center gap-3">
          <span className="text-xs text-blue-300">{heroDate}</span>
          <span className="text-sm font-semibold text-white bg-white/20 hover:bg-white/30 px-4 py-1.5 rounded-full transition">
            Read article →
          </span>
        </div>
      </a>

      {/* Grid of remaining posts */}
      {rest.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {rest.map((post) => (
            <BlogCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}
