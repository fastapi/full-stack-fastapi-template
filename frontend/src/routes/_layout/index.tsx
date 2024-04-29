import { Box, Card, CardBody, Container, Grid, SimpleGrid, Text } from "@chakra-ui/react"
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
          <Card  maxW='sm'>
            <CardBody>
              <Text>Purchase Stock</Text>
            </CardBody>
          </Card>
          <Card  maxW='sm'>
            <CardBody>
              <Text>Purchase Stock</Text>
            </CardBody>
          </Card>
          <Card  maxW='sm'>
            <CardBody>
              <Text>Purchase Stock</Text>
            </CardBody>
          </Card>
          </SimpleGrid>
        </Box>
      </Container>
    </>
  )
}
