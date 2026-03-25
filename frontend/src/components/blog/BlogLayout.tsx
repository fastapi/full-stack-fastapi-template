export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Minimal blog header */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2">
            <img src="/assets/images/Kila_logo.svg" alt="Kila" className="h-7 w-auto" />
            <span className="font-bold text-lg text-slate-900">Kila</span>
          </a>
          <div className="flex items-center gap-4">
            <a href="/blog" className="text-sm text-slate-600 hover:text-slate-900 transition">
              Blog
            </a>
            <a
              href="/"
              className="text-sm font-medium text-blue-600 hover:text-blue-700 transition"
            >
              ← Back to site
            </a>
          </div>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1">{children}</main>

      {/* Blog footer */}
      <footer className="bg-slate-950 text-white py-8 mt-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row justify-between items-center gap-4">
          <span className="text-xs text-slate-400 uppercase tracking-widest">
            © {new Date().getFullYear()} Kila, Inc.
          </span>
          <div className="flex gap-6 text-xs text-slate-400 uppercase tracking-widest">
            <a href="/blog" className="hover:text-white transition">Blog</a>
            <a href="/#pricing" className="hover:text-white transition">Pricing</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
