// src/components/app/AppLayout.tsx

import { useClerk, useUser } from "@clerk/clerk-react"
import { Link, useLocation, useNavigate } from "@tanstack/react-router"
import {
  Activity,
  ChevronDown,
  ChevronRight,
  FolderKanban,
  LogOut,
  Menu,
  PenLine,
  Settings,
  Shield,
  Sparkles,
  Swords,
  TrendingUp,
  User,
  X,
} from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import { ChangePasswordDialog } from "@/components/app/ChangePasswordDialog"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useSubscription } from "@/contexts/SubscriptionContext"
import { useEntitlement } from "@/hooks/useEntitlement"
import type { TierFeatures } from "@/lib/entitlements"
import { TIER_NAMES } from "@/lib/entitlements"

interface MenuItem {
  name: string
  icon: React.ComponentType<{ size?: number }>
  path?: string
  beta?: boolean
  requiredFeature?: keyof TierFeatures
  children?: {
    name: string
    path: string
    hidden?: boolean
    requiredFeature?: keyof TierFeatures
  }[]
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true) // desktop: expanded by default
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false) // mobile: closed by default
  const [expandedMenus, setExpandedMenus] = useState<Set<string>>(new Set())
  const location = useLocation()

  const { signOut } = useClerk()
  const { user: clerkUser } = useUser()
  const userFirstName = clerkUser?.firstName || clerkUser?.username || "User"
  const userFullName =
    clerkUser?.fullName ||
    [clerkUser?.firstName, clerkUser?.lastName].filter(Boolean).join(" ") ||
    userFirstName
  const { isExpired, isReadOnly, tier, canAccess } = useEntitlement()
  const { subscription } = useSubscription()
  const navigate = useNavigate()
  const isOnboarding = location.pathname.includes("/onboarding")

  // Show expiry modal once per browser session
  const SESSION_KEY = "kila_expiry_modal_shown"
  const [expiryModalOpen, setExpiryModalOpen] = useState(false)
  const [changePasswordOpen, setChangePasswordOpen] = useState(false)

  useEffect(() => {
    if (!subscription) return
    const shouldShow =
      (subscription.status === "expired" ||
        subscription.status === "cancelled") &&
      !sessionStorage.getItem(SESSION_KEY)
    if (shouldShow) {
      setExpiryModalOpen(true)
      sessionStorage.setItem(SESSION_KEY, "1")
    }
  }, [subscription])

  // Show full sidebar content when desktop is expanded OR mobile drawer is open
  const showFullContent = sidebarOpen || mobileSidebarOpen

  const isSuperUser = subscription?.is_super_user === true

  const menuItems: MenuItem[] = [
    { name: "Brands", icon: FolderKanban, path: "/app/brands" },
    {
      name: "Brand Impression",
      icon: TrendingUp,
      path: "/app/dashboard/brand-impression",
    },
    {
      name: "Competitive Analysis",
      icon: Swords,
      path: "/app/dashboard/competitors",
    },
    {
      name: "Market Dynamic",
      icon: Activity,
      path: "/app/insight/market-dynamic",
      requiredFeature: "insightAll",
    },
    // TODO: Risk Intelligence hidden — functionality needs revisiting before re-enabling
    // {
    //   name: "Risk Intelligence",
    //   icon: ShieldAlert,
    //   path: "/app/insight/risk-intelligence",
    //   beta: true,
    //   requiredFeature: "insightAll",
    // },
    { name: "Settings", icon: Settings, path: "/app/settings" },
    ...(isSuperUser ? [{ name: "Blog Admin", icon: PenLine, path: "/app/admin/blog" }] : []),
  ]

  const toggleMenu = (name: string) => {
    setExpandedMenus((prev) => {
      const next = new Set(prev)
      if (next.has(name)) {
        next.delete(name)
      } else {
        next.add(name)
      }
      return next
    })
  }

  const handleLogout = async () => {
    try {
      await signOut()
      toast.success("Logged out successfully")
      window.location.href = "/"
    } catch (error) {
      console.error("Logout failed:", error)
      toast.error("Logout failed")
    }
  }

  const closeMobileSidebar = () => setMobileSidebarOpen(false)

  return (
    <div className="h-screen flex bg-slate-50 dark:bg-slate-950 overflow-hidden">
      {/* Mobile backdrop overlay */}
      {mobileSidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={closeMobileSidebar}
          aria-label="Close sidebar overlay"
        />
      )}

      {/* Sidebar */}
      <aside
        className={[
          // Base styles
          "bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800",
          "flex flex-col transition-all duration-300 flex-shrink-0",
          // Mobile: fixed overlay, slides in/out
          "fixed inset-y-0 left-0 z-50 w-fit",
          mobileSidebarOpen ? "translate-x-0" : "-translate-x-full",
          // Desktop: normal flow, toggle width
          "md:relative md:translate-x-0",
          sidebarOpen ? "md:w-[clamp(240px,20vw,320px)]" : "md:w-14",
        ].join(" ")}
      >
        {/* Workspace / User Header */}
        <div className="h-12 flex items-center justify-between px-3 border-b border-slate-200 dark:border-slate-800 flex-shrink-0">
          {showFullContent && (
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                {userFirstName}&apos;s Workspace
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                {userFullName} · Owner
              </p>
            </div>
          )}
          {/* Desktop toggle button */}
          <button
            type="button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden md:block text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 flex-shrink-0"
          >
            {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
          {/* Mobile close button */}
          <button
            type="button"
            onClick={closeMobileSidebar}
            className="md:hidden text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 flex-shrink-0"
          >
            <X size={16} />
          </button>
        </div>

        {/* Subscription Plan Badge */}
        {showFullContent && (
          <div className={`px-3 pt-2.5 pb-1 flex-shrink-0 ${isOnboarding ? "pointer-events-none opacity-40" : ""}`}>
            <button
              type="button"
              onClick={() => navigate({ to: "/app/settings" })}
              className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                tier === "pro"
                  ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/30"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              {tier === "pro" ? (
                <Sparkles size={12} className="text-blue-500 flex-shrink-0" />
              ) : (
                <span className="w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0" />
              )}
              <span>{TIER_NAMES[tier] ?? "Free Trial"} Plan</span>
            </button>
          </div>
        )}

        {/* Navigation */}
        <nav
          className={`flex-1 py-4 space-y-1 overflow-y-auto ${showFullContent ? "px-2" : "px-1"} ${isOnboarding ? "pointer-events-none opacity-40 select-none" : ""}`}
        >
          {menuItems.map((item) => {
            const Icon = item.icon
            const hasChildren = item.children && item.children.length > 0
            const isExpanded = expandedMenus.has(item.name)
            const isParentActive = hasChildren
              ? item.children!.some((child) => location.pathname === child.path)
              : location.pathname === item.path

            if (hasChildren) {
              return (
                <div key={item.name}>
                  <button
                    type="button"
                    onClick={() => {
                      if (showFullContent) {
                        toggleMenu(item.name)
                      } else {
                        setSidebarOpen(true)
                        setExpandedMenus((prev) => new Set(prev).add(item.name))
                      }
                    }}
                    className={`flex items-center w-full py-2 rounded-lg transition ${showFullContent ? "px-3" : "justify-center px-0"} ${
                      isParentActive
                        ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    <Icon size={18} />
                    {showFullContent && (
                      <>
                        <span className="ml-3 text-sm font-medium flex-1 text-left whitespace-nowrap">
                          {item.name}
                        </span>
                        {item.beta && (
                          <span className="ml-1.5 text-[10px] font-semibold uppercase tracking-wide bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded-full">
                            Beta
                          </span>
                        )}
                        {isExpanded ? (
                          <ChevronDown size={12} className="ml-auto" />
                        ) : (
                          <ChevronRight size={12} className="ml-auto" />
                        )}
                      </>
                    )}
                  </button>

                  {showFullContent && isExpanded && (
                    <div className="mt-1 ml-4 space-y-1">
                      {item
                        .children!.filter((child) => !child.hidden)
                        .map((child) => {
                          const isChildActive = location.pathname === child.path
                          const isLocked = child.requiredFeature
                            ? !canAccess(child.requiredFeature)
                            : false

                          if (isLocked) {
                            return (
                              <div
                                key={child.path}
                                className="flex items-center pl-6 pr-3 py-1.5 rounded-lg text-xs text-slate-400 dark:text-slate-600"
                              >
                                <span className="w-1 h-1 rounded-full mr-3 flex-shrink-0 bg-slate-300 dark:bg-slate-600" />
                                <span className="flex-1">{child.name}</span>
                                <button
                                  type="button"
                                  onClick={() =>
                                    navigate({ to: "/app/settings" })
                                  }
                                  title="Upgrade to Pro"
                                  className="flex items-center gap-0.5 text-[10px] font-semibold text-blue-500 hover:text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 px-1.5 py-0.5 rounded-full transition"
                                >
                                  <Sparkles size={9} />
                                  Pro
                                </button>
                              </div>
                            )
                          }

                          return (
                            <Link
                              key={child.path}
                              to={child.path}
                              onClick={closeMobileSidebar}
                              className={`flex items-center pl-6 pr-3 py-1.5 rounded-lg transition text-sm ${
                                isChildActive
                                  ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium"
                                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                              }`}
                            >
                              <span
                                className="w-1 h-1 rounded-full mr-3 flex-shrink-0"
                                style={{
                                  backgroundColor: isChildActive
                                    ? "#2563eb"
                                    : "#94a3b8",
                                }}
                              />
                              {child.name}
                            </Link>
                          )
                        })}
                    </div>
                  )}
                </div>
              )
            }

            const isLocked = item.requiredFeature
              ? !canAccess(item.requiredFeature)
              : false

            if (isLocked) {
              return (
                <div
                  key={item.path}
                  className={`flex items-center py-2 rounded-lg ${showFullContent ? "px-3" : "justify-center px-0"} text-slate-400 dark:text-slate-600`}
                >
                  <Icon size={18} />
                  {showFullContent ? (
                    <>
                      <span className="ml-3 text-sm font-medium whitespace-nowrap flex-1">
                        {item.name}
                      </span>
                      {item.beta && (
                        <span className="mr-1.5 text-[10px] font-semibold uppercase tracking-wide bg-slate-100 dark:bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded-full">
                          Beta
                        </span>
                      )}
                      <button
                        type="button"
                        onClick={() => navigate({ to: "/app/settings" })}
                        title="Upgrade to Pro"
                        className="flex items-center gap-1 text-[10px] font-semibold text-blue-500 hover:text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/40 px-1.5 py-0.5 rounded-full transition"
                      >
                        <Sparkles size={9} />
                        Pro
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      onClick={() => navigate({ to: "/app/settings" })}
                      title="Upgrade to Pro to unlock"
                      className="ml-1 text-blue-400 hover:text-blue-500 transition"
                    >
                      <Sparkles size={10} />
                    </button>
                  )}
                </div>
              )
            }

            return (
              <Link
                key={item.path}
                to={item.path!}
                onClick={closeMobileSidebar}
                className={`flex items-center py-2 rounded-lg transition ${showFullContent ? "px-3" : "justify-center px-0"} ${
                  isParentActive
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                    : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
              >
                <Icon size={18} />
                {showFullContent && (
                  <>
                    <span className="ml-3 text-sm font-medium whitespace-nowrap flex-1">
                      {item.name}
                    </span>
                    {item.beta && (
                      <span className="ml-1.5 text-[10px] font-semibold uppercase tracking-wide bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded-full">
                        Beta
                      </span>
                    )}
                  </>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Sidebar Footer — Kila brand */}
        <div className="border-t border-slate-200 dark:border-slate-800 px-3 py-2.5 flex items-center gap-2 flex-shrink-0">
          <img
            src="/assets/images/Kila_logo.svg"
            alt="Kila"
            className="h-5 w-5 flex-shrink-0"
          />
          {showFullContent && (
            <span className="text-xs text-slate-400 whitespace-nowrap">
              Kila Inc.
            </span>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Bar */}
        <header className="h-12 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center px-4 flex-shrink-0">
          {/* Mobile hamburger */}
          <button
            type="button"
            onClick={() => setMobileSidebarOpen(true)}
            className="md:hidden text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 flex-shrink-0"
          >
            <Menu size={18} />
          </button>

          {/* Avatar with logout dropdown — pushed to the far right */}
          <div className="ml-auto flex-shrink-0">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-1.5 shadow-sm hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  aria-label="Open account menu"
                >
                  <span className="relative">
                    {clerkUser?.imageUrl ? (
                      <img
                        src={clerkUser.imageUrl}
                        alt={userFirstName}
                        className="w-7 h-7 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-7 h-7 bg-gradient-to-br from-blue-600 to-sky-500 rounded-full flex items-center justify-center text-white">
                        <User size={14} />
                      </div>
                    )}
                    <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-500 ring-2 ring-white" />
                  </span>
                  <div className="hidden sm:flex flex-col items-start leading-tight">
                    <span className="text-xs font-semibold text-slate-900">
                      {userFirstName}
                    </span>
                    <span className="text-[11px] text-slate-500">Owner</span>
                  </div>
                  <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="w-64 rounded-xl border border-slate-200 bg-white p-2 shadow-lg"
              >
                <div className="px-2 py-1.5">
                  <p className="text-[11px] uppercase tracking-wide text-slate-400">
                    Signed in as
                  </p>
                  <p className="text-sm font-semibold text-slate-900">
                    {userFullName}
                  </p>
                  <p className="text-xs text-slate-500 truncate">
                    {clerkUser?.primaryEmailAddress?.emailAddress ?? "—"}
                  </p>
                </div>
                <div className="my-1 h-px bg-slate-200" />
                {/* TODO: Account settings — hidden until feature is ready */}
                <DropdownMenuItem
                  onClick={() => setChangePasswordOpen(true)}
                  className="text-sm cursor-pointer"
                >
                  <Shield size={14} className="mr-2 text-slate-500" />
                  Security
                </DropdownMenuItem>
                <div className="my-1 h-px bg-slate-200" />
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="text-sm cursor-pointer text-slate-900 focus:text-slate-900"
                >
                  <LogOut size={14} className="mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Persistent top banner for expired/cancelled */}
        {(isExpired || isReadOnly) && (
          <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-4 py-2 flex items-center justify-between flex-shrink-0">
            <p className="text-xs text-red-800 dark:text-red-300 font-medium">
              {tier === "free_trial"
                ? "Your free trial has ended. Upgrade to Pro to continue full access."
                : "Your Pro subscription is no longer active. Resubscribe to restore access."}
            </p>
            <button
              type="button"
              onClick={() => navigate({ to: "/app/settings" })}
              className="ml-4 text-xs font-semibold text-red-900 dark:text-red-200 underline underline-offset-2 whitespace-nowrap hover:text-red-700"
            >
              {tier === "free_trial" ? "Upgrade to Pro →" : "Resubscribe →"}
            </button>
          </div>
        )}

        {/* Expiry modal — shown once per session on login */}
        <Dialog open={expiryModalOpen} onOpenChange={setExpiryModalOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>
                {tier === "free_trial"
                  ? "Your free trial has ended"
                  : "Your subscription has ended"}
              </DialogTitle>
              <DialogDescription asChild>
                <div className="space-y-3 pt-1">
                  {tier === "free_trial" ? (
                    <>
                      <p>
                        Your 28-day free trial has expired. Your data is safe
                        and your brands are still here.
                      </p>
                      <p>
                        Upgrade to <strong>Pro ($299/month)</strong> to continue
                        monitoring your brand with full access to all features.
                      </p>
                    </>
                  ) : (
                    <>
                      <p>
                        Your Pro subscription is no longer active. Your existing
                        data is preserved.
                      </p>
                      <p>
                        Resubscribe to <strong>Pro ($299/month)</strong> to
                        restore full access. Until then, your account is limited
                        to free trial features.
                      </p>
                    </>
                  )}
                </div>
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="gap-2">
              <Button
                variant="outline"
                onClick={() => setExpiryModalOpen(false)}
              >
                Maybe Later
              </Button>
              <Button
                onClick={() => {
                  setExpiryModalOpen(false)
                  navigate({ to: "/app/settings" })
                }}
              >
                {tier === "free_trial" ? "Upgrade to Pro" : "Resubscribe"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <ChangePasswordDialog
          open={changePasswordOpen}
          onOpenChange={setChangePasswordOpen}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}
