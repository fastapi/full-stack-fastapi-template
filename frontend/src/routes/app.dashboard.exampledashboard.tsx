import { createFileRoute } from '@tanstack/react-router'
import Dashboard from '@/components/app/dashboard/ExampleDashboard'
import ExampleDashboard from "@/components/app/dashboard/ExampleDashboard";

export const Route = createFileRoute('/app/dashboard/exampledashboard')({
  component: ExampleDashboard,
})
