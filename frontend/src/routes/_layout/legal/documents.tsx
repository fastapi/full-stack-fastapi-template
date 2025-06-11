import { createFileRoute } from '@tanstack/react-router'
import DocumentsList from '../../../components/Legal/DocumentsList'

export const Route = createFileRoute('/_layout/legal/documents')({
  component: DocumentsList,
}) 