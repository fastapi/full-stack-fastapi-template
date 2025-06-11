import { createFileRoute } from '@tanstack/react-router'
import TemplateManager from '../../../components/Legal/TemplateManager'

export const Route = createFileRoute('/_layout/legal/templates')({
  component: TemplateManager,
}) 