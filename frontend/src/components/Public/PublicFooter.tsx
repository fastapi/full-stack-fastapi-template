import { Link } from "@tanstack/react-router"
import { Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

interface PublicFooterProps {
  totalRaces?: number
}

export function PublicFooter({ totalRaces = 11248 }: PublicFooterProps) {
  return (
    <footer className="bg-[#0F0E0C] text-white py-14 px-14">
      <div className="container max-w-[1328px]">
        <div className="grid grid-cols-5 gap-8 pb-12">
          {/* Brand column */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="size-5" />
              <span className="text-lg font-black tracking-wide uppercase">VNRUNNER</span>
            </div>
            <p className="text-sm text-white/60 leading-relaxed">
              The AI race finder for runners who know what they want. {totalRaces.toLocaleString()} races indexed across Vietnam.
            </p>
            <div className="flex gap-2 pt-1">
              <Button variant="ghost" size="sm" className="h-[34px] rounded-full bg-white/8 hover:bg-white/12 text-white text-xs font-bold px-3.5">
                App Store
              </Button>
              <Button variant="ghost" size="sm" className="h-[34px] rounded-full bg-white/8 hover:bg-white/12 text-white text-xs font-bold px-3.5">
                Google Play
              </Button>
            </div>
          </div>

          {/* Product */}
          <div className="space-y-3.5">
            <p className="text-xs tracking-[0.14em] uppercase text-white/40 font-mono">Product</p>
            <div className="space-y-2.5 text-sm text-white/75">
              <p className="hover:text-white cursor-pointer transition-colors">AI search</p>
              <p className="hover:text-white cursor-pointer transition-colors">Discover</p>
              <p className="hover:text-white cursor-pointer transition-colors">Compare</p>
              <p className="hover:text-white cursor-pointer transition-colors">Calendar</p>
              <p className="hover:text-white cursor-pointer transition-colors">Mobile app</p>
            </div>
          </div>

          {/* Runners */}
          <div className="space-y-3.5">
            <p className="text-xs tracking-[0.14em] uppercase text-white/40 font-mono">Runners</p>
            <div className="space-y-2.5 text-sm text-white/75">
              <Link to="/signup" className="block hover:text-white transition-colors">
                Sign up
              </Link>
              <p className="hover:text-white cursor-pointer transition-colors">How it works</p>
              <p className="hover:text-white cursor-pointer transition-colors">Pricing</p>
              <p className="hover:text-white cursor-pointer transition-colors">Reviews</p>
              <p className="hover:text-white cursor-pointer transition-colors">Community</p>
            </div>
          </div>

          {/* Organizers */}
          <div className="space-y-3.5">
            <p className="text-xs tracking-[0.14em] uppercase text-white/40 font-mono">Organizers</p>
            <div className="space-y-2.5 text-sm text-white/75">
              <p className="hover:text-white cursor-pointer transition-colors">List your race</p>
              <p className="hover:text-white cursor-pointer transition-colors">Pro dashboard</p>
              <p className="hover:text-white cursor-pointer transition-colors">Analytics</p>
              <p className="hover:text-white cursor-pointer transition-colors">Promotion</p>
            </div>
          </div>

          {/* Company */}
          <div className="space-y-3.5">
            <p className="text-xs tracking-[0.14em] uppercase text-white/40 font-mono">Company</p>
            <div className="space-y-2.5 text-sm text-white/75">
              <p className="hover:text-white cursor-pointer transition-colors">About</p>
              <p className="hover:text-white cursor-pointer transition-colors">Press</p>
              <p className="hover:text-white cursor-pointer transition-colors">Careers</p>
              <p className="hover:text-white cursor-pointer transition-colors">Privacy</p>
              <p className="hover:text-white cursor-pointer transition-colors">Terms</p>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="flex items-center justify-between pt-6 border-t border-white/10">
          <p className="text-xs text-white/50">
            © 2026 Vnrunner · Made for runners
          </p>
          <div className="flex gap-4 text-xs text-white/50">
            <span className="hover:text-white cursor-pointer transition-colors">Privacy</span>
            <span className="hover:text-white cursor-pointer transition-colors">Terms</span>
            <span className="hover:text-white cursor-pointer transition-colors">Cookies</span>
            <span className="hover:text-white cursor-pointer transition-colors">Accessibility</span>
          </div>
          <p className="text-xs text-white/50 font-mono tracking-wider">
            v2.4 · UPDATED 4 MIN AGO
          </p>
        </div>
      </div>
    </footer>
  )
}
