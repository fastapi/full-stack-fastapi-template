// src/components/app/AppLayout.tsx

import { useClerk, useUser } from "@clerk/clerk-react"
import { Link, useLocation } from "@tanstack/react-router"
import {
  ChevronDown,
  ChevronRight,
  FolderKanban,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  User,
  X,
} from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

interface MenuItem {
  name: string
  icon: React.ComponentType<{ size?: number }>
  path?: string
  children?: { name: string; path: string }[]
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true) // desktop: expanded by default
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false) // mobile: closed by default
  const [expandedMenus, setExpandedMenus] = useState<Set<string>>(new Set(["Dashboard"]))
  const location = useLocation()

  const { signOut } = useClerk()
  const { user: clerkUser } = useUser()
  const userFirstName = clerkUser?.firstName || clerkUser?.username || "User"

  // Show full sidebar content when desktop is expanded OR mobile drawer is open
  const showFullContent = sidebarOpen || mobileSidebarOpen

  const menuItems: MenuItem[] = [
    { name: "Projects", icon: FolderKanban, path: "/app/projects" },
    {
      name: "Dashboard",
      icon: LayoutDashboard,
      children: [
        { name: "Brand Overview", path: "/app/dashboard/overview" },
        { name: "Performance Detail", path: "/app/dashboard/performance" },
        { name: "Competitive Analysis", path: "/app/dashboard/competitors" },
      ],
    },
    {
      name: "Insight",
      icon: Lightbulb,
      children: [
        { name: "Brand Risk Overview", path: "/app/insight/brand-risk" },
        { name: "Competitive Risk", path: "/app/insight/competitive-risk" },
        { name: "Growth Risk", path: "/app/insight/growth-risk" },
        { name: "Ranking Position Risk", path: "/app/insight/ranking-risk" },
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
          "fixed inset-y-0 left-0 z-50 w-64",
          mobileSidebarOpen ? "translate-x-0" : "-translate-x-full",
          // Desktop: normal flow, toggle width
          "md:relative md:translate-x-0",
          sidebarOpen ? "md:w-64" : "md:w-20",
        ].join(" ")}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          {showFullContent ? (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                Kila
              </span>
            </div>
          ) : (
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">K</span>
            </div>
          )}
          {/* Desktop toggle button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden md:block text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          {/* Mobile close button */}
          <button
            onClick={closeMobileSidebar}
            className="md:hidden text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
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
                    className={`flex items-center w-full px-3 py-2 rounded-lg transition ${
                      isParentActive
                        ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }`}
                  >
                    <Icon size={20} />
                    {showFullContent && (
                      <>
                        <span className="ml-3 font-medium flex-1 text-left">{item.name}</span>
                        {isExpanded ? (
                          <ChevronDown size={16} className="ml-auto" />
                        ) : (
                          <ChevronRight size={16} className="ml-auto" />
                        )}
                      </>
                    )}
                  </button>

                  {showFullContent && isExpanded && (
                    <div className="mt-1 ml-4 space-y-1">
                      {item.children!.map((child) => {
                        const isChildActive = location.pathname === child.path
                        return (
                          <Link
                            key={child.path}
                            to={child.path}
                            onClick={closeMobileSidebar}
                            className={`flex items-center pl-6 pr-3 py-1.5 rounded-lg transition text-sm ${
                              isChildActive
                                ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium"
                                : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                            }`}
                          >
                            <span
                              className="w-1.5 h-1.5 rounded-full mr-3 flex-shrink-0"
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
                className={`flex items-center px-3 py-2 rounded-lg transition ${
                  isParentActive
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <Icon size={20} />
                {showFullContent && <span className="ml-3 font-medium">{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        {/* User Section */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex-shrink-0">
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
          >
            <LogOut size={20} />
            {showFullContent && <span className="ml-3">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Bar */}
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center px-4 gap-3 flex-shrink-0">
          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileSidebarOpen(true)}
            className="md:hidden text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex-shrink-0"
          >
            <Menu size={22} />
          </button>

          {/* Search Bar */}
          <div className="flex-1 min-w-0 max-w-2xl">
            <input
              type="text"
              placeholder="Search..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
            />
          </div>

          {/* User Profile */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <span className="text-sm font-medium text-gray-900 dark:text-white hidden sm:block">
              {userFirstName}
            </span>
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
              <User size={18} />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}
