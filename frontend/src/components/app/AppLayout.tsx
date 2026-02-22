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
  Search,
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
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedMenus, setExpandedMenus] = useState<Set<string>>(new Set(["Dashboard"]))
  const location = useLocation()

  const { signOut } = useClerk()
  const { user: clerkUser } = useUser()
  const userFirstName = clerkUser?.firstName || clerkUser?.username || "User"

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

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
          {sidebarOpen ? (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
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
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1">
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
                  {/* Parent item - toggles expand/collapse */}
                  <button
                    onClick={() => {
                      if (sidebarOpen) {
                        toggleMenu(item.name)
                      } else {
                        // When sidebar is collapsed, expand sidebar and menu
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
                    {sidebarOpen && (
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

                  {/* Child items */}
                  {sidebarOpen && isExpanded && (
                    <div className="mt-1 ml-4 space-y-1">
                      {item.children!.map((child) => {
                        const isChildActive = location.pathname === child.path
                        return (
                          <Link
                            key={child.path}
                            to={child.path}
                            className={`flex items-center pl-6 pr-3 py-1.5 rounded-lg transition text-sm ${
                              isChildActive
                                ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium"
                                : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                            }`}
                          >
                            <span className="w-1.5 h-1.5 rounded-full mr-3 flex-shrink-0" style={{
                              backgroundColor: isChildActive ? "#3b82f6" : "#9ca3af",
                            }} />
                            {child.name}
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            }

            // Simple item (no children)
            return (
              <Link
                key={item.path}
                to={item.path!}
                className={`flex items-center px-3 py-2 rounded-lg transition ${
                  isParentActive
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <Icon size={20} />
                {sidebarOpen && (
                  <span className="ml-3 font-medium">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* User Section */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
          >
            <LogOut size={20} />
            {sidebarOpen && <span className="ml-3">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6">
          {/* Search Bar */}
          <div className="flex-1 max-w-2xl">
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                size={20}
              />
              <input
                type="text"
                placeholder="Search..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* User Profile */}
          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {userFirstName}
              </div>
            </div>
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
              <User size={20} />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
