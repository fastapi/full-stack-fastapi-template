import { marked } from "marked"
import type { BlogPostPublicResponse } from "@/clients/blog"

interface BlogPostPageProps {
  post: BlogPostPublicResponse
}

const CATEGORY_TEXT: Record<string, string> = {
  GEO: "text-blue-300",
  SEO: "text-amber-300",
  STRATEGY: "text-green-300",
}

export default function BlogPostPage({ post }: BlogPostPageProps) {
  const formattedDate = new Date(post.published_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  const htmlContent = marked.parse(post.content, { async: false })
  const categoryColor = CATEGORY_TEXT[post.category] ?? "text-slate-300"

  return (
    <article>
      {/* Dark hero banner */}
      <div className="bg-gradient-to-br from-[#1e3a5f] to-[#1e40af] px-4 sm:px-6 py-14">
        <div className="max-w-2xl mx-auto text-center">
          <div className={`text-xs font-semibold uppercase tracking-widest mb-4 ${categoryColor}`}>
            {post.category} · {post.read_time_minutes} min read
          </div>
          <h1 className="text-2xl sm:text-4xl font-bold text-white leading-tight mb-4">
            {post.title}
          </h1>
          <div className="text-sm text-blue-200">
            {post.author_name} · {formattedDate}
          </div>
        </div>
      </div>

      {/* Back link */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 mt-8">
        <a href="/blog" className="text-sm text-blue-600 hover:underline">← Back to Blog</a>
      </div>

      {/* Centered markdown content — basic styling without prose plugin */}
      <div
        className="max-w-2xl mx-auto px-4 sm:px-6 py-8 [&>h1]:text-2xl [&>h1]:font-bold [&>h1]:text-slate-900 [&>h1]:mt-8 [&>h1]:mb-4 [&>h2]:text-xl [&>h2]:font-bold [&>h2]:text-slate-900 [&>h2]:mt-6 [&>h2]:mb-3 [&>h3]:text-lg [&>h3]:font-semibold [&>h3]:text-slate-900 [&>h3]:mt-5 [&>h3]:mb-2 [&>p]:text-slate-700 [&>p]:leading-relaxed [&>p]:mb-4 [&>ul]:list-disc [&>ul]:pl-6 [&>ul]:mb-4 [&>ul>li]:text-slate-700 [&>ul>li]:mb-1 [&>ol]:list-decimal [&>ol]:pl-6 [&>ol]:mb-4 [&>ol>li]:text-slate-700 [&>ol>li]:mb-1 [&>blockquote]:border-l-4 [&>blockquote]:border-blue-300 [&>blockquote]:pl-4 [&>blockquote]:italic [&>blockquote]:text-slate-600 [&>blockquote]:mb-4 [&>pre]:bg-slate-100 [&>pre]:rounded-lg [&>pre]:p-4 [&>pre]:overflow-x-auto [&>pre]:mb-4 [&>code]:bg-slate-100 [&>code]:rounded [&>code]:px-1 [&>code]:text-sm [&>img]:rounded-lg [&>img]:mb-4 [&_a]:text-blue-600 [&_a]:hover:underline"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />

      {/* CTA card */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 pb-16">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-2xl p-8 text-center">
          <h3 className="text-xl font-bold text-slate-900 mb-2">
            Track how your brand appears in AI search
          </h3>
          <p className="text-slate-600 text-sm mb-5">
            Measure mention frequency, sentiment, and competitive positioning in real time.
          </p>
          <a
            href="https://www.spekila.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-6 py-2.5 rounded-full transition"
          >
            Start free 4-week trial →
          </a>
        </div>
      </div>

      {/* Bottom back link */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 pb-8">
        <a href="/blog" className="text-sm text-blue-600 hover:underline">← Back to Blog</a>
      </div>
    </article>
  )
}
