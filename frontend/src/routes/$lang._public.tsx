import { createFileRoute, Outlet } from "@tanstack/react-router"
import { PublicFooter } from "@/components/Public/PublicFooter"
import { PublicHeader } from "@/components/Public/PublicHeader"

export const Route = createFileRoute("/$lang/_public")({
  component: PublicLayout,
})

function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <PublicHeader />
      <main className="flex-1">
        <Outlet />
      </main>
      <PublicFooter />
    </div>
  )
}
