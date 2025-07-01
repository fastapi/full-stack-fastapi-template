import { createFileRoute, redirect } from '@tanstack/react-router'
import { SignInPage } from '../components/Common/ClerkAuth'

export const Route = createFileRoute('/sign-in')({
  component: SignInPage,
}) 