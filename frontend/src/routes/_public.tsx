import { createFileRoute, Outlet } from "@tanstack/react-router"
import { PublicHeader } from "@/components/Public/PublicHeader"
import { PublicFooter } from "@/components/Public/PublicFooter"

export const Route = createFileRoute("/_public")({
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

export default PublicLayout
