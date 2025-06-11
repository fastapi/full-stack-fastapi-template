import { createFileRoute } from '@tanstack/react-router'
import DocumentGenerator from '../../../components/Legal/DocumentGenerator'

export const Route = createFileRoute('/_layout/legal/generator')({
  component: DocumentGenerator,
}) 