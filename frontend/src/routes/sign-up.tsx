import { createFileRoute } from '@tanstack/react-router'
import { SignUpPage } from '../components/Common/ClerkAuth'

export const Route = createFileRoute('/sign-up')({
  component: SignUpPage,
}) 