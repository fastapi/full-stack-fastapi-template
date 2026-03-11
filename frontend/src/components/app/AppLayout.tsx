// src/components/app/AppLayout.tsx

import { useClerk, useUser } from "@clerk/clerk-react"
import { Link, useLocation } from "@tanstack/react-router"
import {
  ChevronDown,
  ChevronRight,
  FolderKanban,
  Lightbulb,
  Lock,
  LogOut,
  Menu,
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
  const { isExpired, canAccess } = useEntitlement()

  // Show full sidebar content when desktop is expanded OR mobile drawer is open
  const showFullContent = sidebarOpen || mobileSidebarOpen

  const menuItems: MenuItem[] = [
    { name: "Brands", icon: FolderKanban, path: "/app/brands" },
    { name: "Brand Impression", icon: TrendingUp, path: "/app/dashboard/brand-impression" },
    { name: "Competitive Analysis", icon: Swords, path: "/app/dashboard/competitors" },
    {
      name: "Insight",
      icon: Lightbulb,
      beta: true,
      children: [
        { name: "Market Dynamic", path: "/app/insight/market-dynamic", requiredFeature: "insightAll" },
        { name: "Risk Intelligence", path: "/app/insight/risk-intelligence", requiredFeature: "insightAll" },
      ],
    },
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
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900 overflow-hidden">
      {/* Mobile backdrop overlay */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={closeMobileSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={[
          // Base styles
          "bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700",
          "flex flex-col transition-all duration-300 flex-shrink-0",
          // Mobile: fixed overlay, slides in/out
          "fixed inset-y-0 left-0 z-50 w-fit",
          mobileSidebarOpen ? "translate-x-0" : "-translate-x-full",
          // Desktop: normal flow, toggle width
          "md:relative md:translate-x-0",
          sidebarOpen ? "md:w-1/4" : "md:w-12",
        ].join(" ")}
      >
        {/* Workspace / User Header */}
        <div className="flex items-center justify-between px-3 py-3 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          {showFullContent && (
            <div className="flex items-center gap-1.5 min-w-0">
              <span className="text-[11px] font-semibold text-gray-900 dark:text-white whitespace-nowrap">
                {userFirstName}
              </span>
              <span className="text-[11px] font-semibold text-gray-900 dark:text-white whitespace-nowrap">Workspace</span>
            </div>
          )}
          {/* Desktop toggle button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden md:block text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex-shrink-0"
          >
            {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
          {/* Mobile close button */}
          <button
            onClick={closeMobileSidebar}
            className="md:hidden text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex-shrink-0"
          >
            <X size={16} />
          </button>
        </div>

        {/* Navigation */}
        <nav className={`flex-1 py-4 space-y-1 overflow-y-auto ${showFullContent ? "px-2" : "px-1"}`}>
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
                    onClick={() => {
                      if (showFullContent) {
                        toggleMenu(item.name)
                      } else {
                        setSidebarOpen(true)
                        setExpandedMenus((prev) => new Set(prev).add(item.name))
                      }
                    }}
                    className={`flex items-center w-full py-1.5 rounded-lg transition ${showFullContent ? "px-3" : "justify-center px-0"} ${
                      isParentActive
                        ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }`}
                  >
                    <Icon size={18} />
                    {showFullContent && (
                      <>
                        <span className="ml-3 text-xs font-medium flex-1 text-left whitespace-nowrap">{item.name}</span>
                        {item.beta && (
                          <span className="ml-1.5 text-[9px] font-semibold uppercase tracking-wide bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 px-1 py-0.5 rounded">
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
                      {item.children!.filter((child) => !child.hidden).map((child) => {
                        const isChildActive = location.pathname === child.path
                        const isLocked = child.requiredFeature
                          ? !canAccess(child.requiredFeature)
                          : false

                        if (isLocked) {
                          return (
                            <div
                              key={child.path}
                              className="flex items-center pl-6 pr-3 py-1 rounded-lg text-xs text-gray-400 dark:text-gray-600 cursor-not-allowed select-none"
                            >
                              <span className="w-1 h-1 rounded-full mr-3 flex-shrink-0 bg-gray-300 dark:bg-gray-600" />
                              {child.name}
                              <Lock size={10} className="ml-auto opacity-50" />
                            </div>
                          )
                        }

                        return (
                          <Link
                            key={child.path}
                            to={child.path}
                            onClick={closeMobileSidebar}
                            className={`flex items-center pl-6 pr-3 py-1 rounded-lg transition text-xs ${
                              isChildActive
                                ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium"
                                : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                            }`}
                          >
                            <span
                              className="w-1 h-1 rounded-full mr-3 flex-shrink-0"
                              style={{ backgroundColor: isChildActive ? "#3b82f6" : "#9ca3af" }}
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
                className={`flex items-center py-1.5 rounded-lg transition ${showFullContent ? "px-3" : "justify-center px-0"} ${
                  isParentActive
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <Icon size={18} />
                {showFullContent && <span className="ml-3 text-xs font-medium whitespace-nowrap">{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Sidebar Footer — Kila brand */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-3 py-2.5 flex items-center gap-2 flex-shrink-0">
          <img
            src="/assets/images/Kila_logo.svg"
            alt="Kila"
            className="h-5 w-5 flex-shrink-0"
          />
          {showFullContent && (
            <span className="text-[10px] text-gray-400 whitespace-nowrap">Kila Inc.</span>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Bar */}
        <header className="h-12 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center px-4 flex-shrink-0">
          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileSidebarOpen(true)}
            className="md:hidden text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex-shrink-0"
          >
            <Menu size={18} />
          </button>

          {/* Avatar with logout dropdown — pushed to the far right */}
          <div className="ml-auto flex-shrink-0">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
                  {clerkUser?.imageUrl ? (
                    <img
                      src={clerkUser.imageUrl}
                      alt={userFirstName}
                      className="w-7 h-7 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white">
                      <User size={14} />
                    </div>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-24 min-w-0">
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="text-xs cursor-pointer text-red-600 focus:text-red-600"
                >
                  <LogOut size={13} className="mr-2" />
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
              Your free trial has ended. Your data is safe — upgrade to continue monitoring your brand.
            </p>
            <a
              href="/pricing"
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
