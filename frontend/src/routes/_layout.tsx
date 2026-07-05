import { createFileRoute, Outlet } from "@tanstack/react-router"
// import { isLoggedIn } from "@/hooks/useAuth"

import { Footer } from "@/components/Common/Footer"
import { Logo } from "@/components/Common/Logo"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { FiltersProvider } from "@/context/filters"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  //   beforeLoad: async () => {
  //     if (!isLoggedIn()) {
  //       throw redirect({
  //         to: "/login",
  //       })
  //     }
  //   },
})

function Layout() {
  return (
    <FiltersProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="sticky top-0 z-10 flex h-12 shrink-0 items-center gap-2 border-b bg-background px-4">
            <SidebarTrigger className="-ml-1 text-muted-foreground" />
            <Logo expandable className="md:hidden" />
          </header>
          <main className="flex-1 p-6 md:p-8">
            <div className="mx-auto max-w-3xl">
              <Outlet />
            </div>
          </main>
          <Footer />
        </SidebarInset>
      </SidebarProvider>
    </FiltersProvider>
  )
}
