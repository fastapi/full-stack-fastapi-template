"use client"

import { Home, Package, Settings, Shield, Search } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar"

const menuItems = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Items",
    url: "/dashboard/items",
    icon: Package,
  },
  {
    title: "ColPali Search",
    url: "/dashboard/colpali",
    icon: Search,
  },
  {
    title: "User Settings",
    url: "/dashboard/settings",
    icon: Settings,
  },
  {
    title: "Admin",
    url: "/dashboard/users",
    icon: Shield,
  },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar className="border-r bg-white dark:bg-slate-900">
      <SidebarHeader className="p-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-teal-600 rounded-full flex items-center justify-center">
            <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
              <div className="w-2.5 h-2.5 bg-teal-600 rounded-full"></div>
            </div>
          </div>
          <span className="text-xl font-bold text-teal-600">FastAPI</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.url}
                    className="text-gray-700 dark:text-gray-300 hover:text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-900/20"
                  >
                    <Link href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-6">
        <div className="text-sm text-gray-500 dark:text-gray-400">
          <p>Logged in as:</p>
          <p className="font-medium">admin@example.com</p>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
