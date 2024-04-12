import {
  Container,
  Flex,
  Heading,
  Skeleton,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { ItemsService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"

export const Route = createFileRoute("/_layout/items")({
  component: Items,
})

function ItemsTable() {
  const { data: items } = useSuspenseQuery({
    queryKey: ["items"],
    queryFn: () => ItemsService.readItems({}),
  })
  return (
    <TableContainer>
      <Table size={{ base: "sm", md: "md" }}>
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>Title</Th>
            <Th>Description</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {items.data.map((item) => (
            <Tr key={item.id}>
              <Td>{item.id}</Td>
              <Td>{item.title}</Td>
              <Td color={!item.description ? "ui.dim" : "inherit"}>
                {item.description || "N/A"}
              </Td>
              <Td>
                <ActionsMenu type={"Item"} value={item} />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  )
}

function Items() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Items Management
      </Heading>

      <ErrorBoundary fallback={<div>Something went wrong</div>}>
        <Suspense
          fallback={
            <Flex py={8} gap={4}>
              <Skeleton height="40px" width={100} />
            </Flex>
          }
        >
          <Navbar type={"Item"} />
          <ItemsTable />
        </Suspense>
      </ErrorBoundary>
    </Container>
  )
}
