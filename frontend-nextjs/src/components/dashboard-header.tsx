"use client"

import { Bell, User, LogOut, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { ThemeToggle } from "@/components/theme-toggle"
import { useRouter } from "next/navigation"
import { clearAuthTokens } from "@/lib/auth"

export function DashboardHeader() {
  const router = useRouter()

  const handleLogout = () => {
    // Clear authentication tokens/data
    clearAuthTokens()
    // Redirect to login page
    router.push('/login')
  }

  const handleProfile = () => {
    router.push('/dashboard/settings')
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white dark:bg-slate-900 px-6">
      <div className="flex items-center space-x-4">
        <SidebarTrigger />
      </div>

      <div className="flex items-center">
        <ThemeToggle />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative rounded-full">
              <div className="h-8 w-8 rounded-full bg-teal-600 flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuItem onClick={handleProfile}>
              <Settings className="mr-2 h-4 w-4" />
              <span>Profile Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
