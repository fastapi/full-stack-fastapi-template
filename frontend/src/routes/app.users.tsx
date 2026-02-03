import { createFileRoute } from '@tanstack/react-router'
import UserManagement from '@/components/app/UserManagement'

export const Route = createFileRoute('/app/users')({
  component: UserManagement,
})
