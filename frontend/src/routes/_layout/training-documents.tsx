import { createFileRoute } from "@tanstack/react-router"
import { TrainingDocumentsManagement } from "../../components/Training/TrainingDocumentsManagement"

export const Route = createFileRoute("/_layout/training-documents")({
  component: TrainingDocumentsManagement,
})
