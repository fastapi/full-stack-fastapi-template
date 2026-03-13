// src/components/app/AppLayout.tsx

import { useClerk, useUser } from "@clerk/clerk-react"
import { Link, useLocation } from "@tanstack/react-router"
import {
  ChevronDown,
  ChevronRight,
  CreditCard,
  DollarSign,
  FolderKanban,
  Lightbulb,
  Lock,
  LogOut,
  Menu,
  Shield,
  Swords,
  TrendingUp,
  User,
  X,
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useEntitlement } from "@/hooks/useEntitlement"
import type { TierFeatures } from "@/lib/entitlements"

interface MenuItem {
  name: string
  icon: React.ComponentType<{ size?: number }>
  path?: string
  beta?: boolean
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
  const { isExpired, canAccess, tier: currentTier } = useEntitlement()

  // Show full sidebar content when desktop is expanded OR mobile drawer is open
  const showFullContent = sidebarOpen || mobileSidebarOpen

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
      name: "Insight",
      icon: Lightbulb,
      beta: true,
      children: [
        {
          name: "Market Dynamic",
          path: "/app/insight/market-dynamic",
          requiredFeature: "insightAll",
        },
        {
          name: "Risk Intelligence",
          path: "/app/insight/risk-intelligence",
          requiredFeature: "insightAll",
        },
      ],
    },
    { name: "Pricing", icon: DollarSign, path: "/app/pricing" },
    ...(currentTier !== "free_trial"
      ? [{ name: "Billing", icon: CreditCard, path: "/app/billing" } as MenuItem]
      : []),
    { name: "My Profile", icon: User, path: "/app/users" },
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
          sidebarOpen
            ? "md:w-[clamp(240px,20vw,320px)]"
            : "md:w-14",
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

        {/* Navigation */}
        <nav
          className={`flex-1 py-4 space-y-1 overflow-y-auto ${showFullContent ? "px-2" : "px-1"}`}
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
                                className="flex items-center pl-6 pr-3 py-1.5 rounded-lg text-xs text-slate-400 dark:text-slate-600 cursor-not-allowed select-none"
                              >
                                <span className="w-1 h-1 rounded-full mr-3 flex-shrink-0 bg-slate-300 dark:bg-slate-600" />
                                {child.name}
                                <Lock
                                  size={10}
                                  className="ml-auto opacity-50"
                                />
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
                  <span className="ml-3 text-sm font-medium whitespace-nowrap">
                    {item.name}
                  </span>
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
                <DropdownMenuItem className="text-sm">
                  <User size={14} className="mr-2 text-slate-500" />
                  Account settings
                </DropdownMenuItem>
                <DropdownMenuItem className="text-sm">
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

        {/* Trial expiry banner */}
        {isExpired && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-700 px-4 py-2 flex items-center justify-between flex-shrink-0">
            <p className="text-xs text-amber-800 dark:text-amber-300 font-medium">
              Your free trial has ended. Your data is safe — upgrade to continue
              monitoring your brand.
            </p>
            <a
              href="/app/pricing"
              className="ml-4 text-xs font-semibold text-amber-900 dark:text-amber-200 underline underline-offset-2 whitespace-nowrap hover:text-amber-700"
            >
              View plans →
            </a>
          </div>
        )}

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}
