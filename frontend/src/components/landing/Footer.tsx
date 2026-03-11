// src/components/landing/Footer.tsx
import { Facebook, Instagram, Linkedin, Twitter, Youtube } from "lucide-react"

export default function Footer() {
  return (
    <footer className="bg-slate-950 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6 font-body text-xs tracking-[0.2em] uppercase text-slate-400">
            <span>© 2026 Kila, Inc. All Rights Reserved</span>
            <a href="#privacy" className="hover:text-white transition">
              Privacy Policy
            </a>
            <a href="#terms" className="hover:text-white transition">
              Terms of Service
            </a>
            <a href="#cookies" className="hover:text-white transition">
              Cookie Settings
            </a>
          </div>

          <div className="flex items-center space-x-4">
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
            >
              <Linkedin size={20} />
            </a>
            <a
              href="https://youtube.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
            >
              <Youtube size={20} />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
            >
              <Twitter size={20} />
            </a>
            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
            >
              <Instagram size={20} />
            </a>
            <a
              href="https://tiktok.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <title>TikTok</title>
                <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
              </svg>
            </a>
            <a
              href="https://facebook.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition"
            >
              <Facebook size={20} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
