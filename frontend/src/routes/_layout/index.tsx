import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import HomePage from '../../pages/HomePage'

import { useAuth } from '@/hooks/useAuth'
import { RouteGuard } from '@/components/Common/RouteGuard'
import { CEODashboard } from '@/components/Admin/CEODashboard'
import { ManagerDashboard } from '@/components/Admin/ManagerDashboard'
import { SupervisorDashboard } from '@/components/Admin/SupervisorDashboard'
import { HRDashboard } from '@/components/Admin/HRDashboard'
import { SupportDashboard } from '@/components/Admin/SupportDashboard'
import { AgentDashboard } from '@/components/Admin/AgentDashboard'

export const Route = createFileRoute('/_layout/')({
  component: HomePage,
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl" truncate maxW="sm">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text>
        </Box>
      </Container>
    </>
  )
}
