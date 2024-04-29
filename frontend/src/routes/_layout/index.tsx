import { Box, Card, CardBody, Container, Grid, Link, SimpleGrid, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import type { UserPublic } from "../../client"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const queryClient = useQueryClient()

  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text>
        </Box>

        <Box pt={12} m={4}>
          <Text fontSize="2xl">
           Quick Actions 🛠️
          </Text>
          <SimpleGrid spacing={4} templateColumns='repeat(auto-fill, minmax(200px, 1fr))'>
          <Card  maxW='s'>
            <CardBody>
              <Link href="/stores" color='teal.500'>Visit Stores and Purchase</Link>
            </CardBody>
          </Card>
          <Card  maxW='sm'>
            <CardBody>
            <Link href="/warehouse" color='teal.500'>Visit warehouse</Link>
            </CardBody>
          </Card>
          </SimpleGrid>
        </Box>
      </Container>
    </>
  )
}
