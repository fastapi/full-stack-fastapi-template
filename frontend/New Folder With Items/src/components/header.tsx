import { Link } from "@tanstack/react-router"
import { ArrowRight } from "lucide-react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import AuthModal from "@/components/Auth/AuthModal"
import { isLoggedIn } from "@/hooks/useAuth"
import { Appearance } from "./Common/Appearance"
import { LanguageSwitcher } from "./Common/LanguageSwitcher"
import { Logo } from "./Common/Logo"

export default function Header() {
  const [authOpen, setAuthOpen] = useState(false)
  const [authTab, setAuthTab] = useState<"signin" | "signup">("signin")
  const { t } = useTranslation()
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Left — Logo */}
          <Link to="/" className="flex items-center shrink-0">
            <Logo variant="full" className="h-24" asLink={false} />
          </Link>

          {/* Centre — Nav links */}
          <nav className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
            <a
              href="/#features"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {t("nav.features")}
            </a>
            <Link
              to="/pricing"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {t("nav.pricing")}
            </Link>
            <a
              href="/#how"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {t("nav.howItWorks")}
            </a>
            <a
              href="/#faq"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {t("nav.faq")}
            </a>
          </nav>

          {/* Right — Actions */}
          <div className="flex items-center gap-4 shrink-0">
            <LanguageSwitcher />
            <Appearance />
            {!isLoggedIn() ? (
              <>
                {/* Controlled Auth modal - clicking buttons opens the dialog with the right tab */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthTab("signin")
                    setAuthOpen(true)
                  }}
                  className="hidden sm:inline-flex text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  {t("nav.signIn")}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAuthTab("signup")
                    setAuthOpen(true)
                  }}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                  {t("nav.signUp")}
                </button>
                <AuthModal
                  open={authOpen}
                  setOpen={setAuthOpen}
                  initialTab={authTab}
                />
              </>
            ) : (
              <Link
                to="/dashboard"
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <div className="flex items-center gap-2">
                  {t("nav.dashboard")}
                  <ArrowRight className="w-4 h-4" />
                </div>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
