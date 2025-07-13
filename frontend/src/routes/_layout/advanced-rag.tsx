import { createFileRoute } from "@tanstack/react-router"
import { AdvancedRAGManagement } from "../../components/Admin/AdvancedRAGManagement"
import { RoleGuard } from "../../components/Common/RoleGuard"

export const Route = createFileRoute("/_layout/advanced-rag")({
  component: AdvancedRAG,
})

function AdvancedRAG() {
  return (
    <RoleGuard permission="admin">
      <AdvancedRAGManagement />
    </RoleGuard>
  )
}
