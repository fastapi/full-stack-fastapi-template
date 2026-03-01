import { Link } from "@tanstack/react-router"
import {
  Briefcase,
  FileText,
  History,
  Home,
  Sparkles,
  Users,
} from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import { Button } from "@/components/ui/button"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: FileText, title: "Templates", path: "/templates" },
  { icon: Briefcase, title: "Editor", path: "/template-editor" },
  { icon: Sparkles, title: "Generate", path: "/generate" },
  { icon: History, title: "History", path: "/history" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()
  const { state, toggleSidebar } = useSidebar()

  const items = currentUser?.is_superuser
    ? [...baseItems, { icon: Users, title: "Admin", path: "/admin" }]
    : baseItems

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-3 py-4">
        <div className="flex items-center justify-between gap-2 group-data-[collapsible=icon]:justify-center">
          {state === "collapsed" ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-9 rounded-xl"
              onClick={toggleSidebar}
              aria-label="Open sidebar"
              title="Open sidebar"
            >
              <Logo variant="icon" asLink={false} />
            </Button>
          ) : (
            <>
              <Link
                to="/"
                className="inline-flex items-center rounded-[var(--radius-control)] px-1 py-1 outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <Logo variant="full" asLink={false} />
                <span className="sr-only">Go to dashboard</span>
              </Link>
              <SidebarTrigger
                className="text-muted-foreground hover:text-foreground size-9 rounded-xl"
                aria-label="Collapse sidebar"
                title="Collapse sidebar"
              />
            </>
          )}
        </div>
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
