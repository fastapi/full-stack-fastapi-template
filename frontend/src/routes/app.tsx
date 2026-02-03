import { createFileRoute, Outlet, redirect } from '@tanstack/react-router'
import AppLayout from '@/components/app/AppLayout'

export const Route = createFileRoute('/app')({
  beforeLoad: ({ context, location }) => {
    // Check if user is authenticated
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'

    if (!isAuthenticated) {
      throw redirect({
        to: '/',
        search: {
          redirect: location.href,
        },
      })
    }
  },
  component: () => (
    <AppLayout>
      <Outlet />
    </AppLayout>
  ),
})
