import {
  Container,
  Flex,
  Heading,
  Text,
  Skeleton,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  Box,
  SimpleGrid,
  CardBody,
  Card,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useParams } from "@tanstack/react-router"

import { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { ItemPublic, StoresService } from "../../client"
import Navbar from "../../components/Common/Navbar"
import ActionsMenu from "../../components/Common/ActionsMenu"

export const Route = createFileRoute("/_layout/store/$storeId/inventory")({
  component: Inventory,
})

function InventoryTableBody({items}: {items: ItemPublic[]}) {

  return (
    <Tbody>
      {items.map((item) => ( // Update warehouse variable name
        <Tr key={item.id}>
          <Td>{item.title} </Td>
          <Td>{item.units} </Td>
          <Td>{Number(item.revenue) * Number(item.units)} </Td>
          <Td>{Number(item.cost) * Number(item.units)} </Td>
          <Td>
          <ActionsMenu type={"StoreInventory"} value={item} />
        </Td>
        </Tr>
      ))}
    </Tbody>
  )
}

function InventoryTable({items}: {items: ItemPublic[]}) {

  return (
    <TableContainer>
      <Table size={{ base: "sm", md: "md" }}>
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Units</Th>
            <Th>Total Revenue</Th>
            <Th>Total Cost</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <ErrorBoundary
          fallbackRender={({ error }) => (
            <Tbody>
              <Tr>
                <Td colSpan={4}>Something went wrong: {error.message}</Td>
              </Tr>
            </Tbody>
          )}
        >
          <Suspense
            fallback={
              <Tbody>
                {new Array(2).fill(null).map((_, index) => (
                  <Tr key={index}>
                    {new Array(7).fill(null).map((_, index) => (
                      <Td key={index}>
                        <Flex>
                          <Skeleton height="20px" width="20px" />
                        </Flex>
                      </Td>
                    ))}
                  </Tr>
                ))}
              </Tbody>
            }
          >
            <InventoryTableBody items={items}/>
          </Suspense>
        </ErrorBoundary>
      </Table>
    </TableContainer>
  )
}

function Inventory() {
  const params = useParams({
      from: "/_layout/store/$storeId/inventory"
  })

  const { data: stores } = useQuery({
    queryKey: ["inventory"],
    queryFn: () => StoresService.readStoreInventory({
      id: Number(params.storeId)
    }), 
  })

  const totalRevenue = stores?.data.reduce((acc: number, item) => acc + (Number(item.revenue) * Number(item.units)), 0)
  const totalCost= stores?.data?.reduce((acc: number, item) => acc + (Number(item.cost) * Number(item.units)), 0)



  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Inventory Management for {params.storeId}
      </Heading>
      <Navbar type="Inventory" />
      <Box pt={12} m={4}>
        <SimpleGrid
          spacing={4}
          templateColumns="repeat(auto-fill, minmax(200px, 1fr))"
        >
          <Card maxW="s">
            <CardBody>
              <Text>
                Total Revenue: 💰{totalRevenue ?? 0}
              </Text>
            </CardBody>
          </Card>
          <Card maxW="sm">
            <CardBody>
            <Text>
                Total Cost: 💰{totalCost ?? 0}
              </Text>
            </CardBody>
          </Card>
        </SimpleGrid>
      </Box>
      <Text fontSize="xs">Hint: use actions to purchase</Text>
      <br />
      {stores && <InventoryTable items={stores.data} />}
    </Container>
  );
}

