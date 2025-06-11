import { createFileRoute } from '@tanstack/react-router'
import LegalDashboard from '../../../components/Legal/LegalDashboard'

export const Route = createFileRoute('/_layout/legal/')({
  component: LegalDashboard,
}) 