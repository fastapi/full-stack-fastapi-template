import {
    Container,
    Flex,
    Heading,
    Link,
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
  import { createFileRoute, useParams } from "@tanstack/react-router"
  
  import { Suspense } from "react"
  import { ErrorBoundary } from "react-error-boundary"
  import { StoresService } from "../../client"
import Navbar from "../../components/Common/Navbar"
import ActionsMenu from "../../components/Common/ActionsMenu"
  
  export const Route = createFileRoute("/_layout/store/$storeId/inventory")({
    component: Inventory,
  })
  
  function InventoryTableBody({storeId}: {storeId: string}) {
    const { data: stores } = useSuspenseQuery({
      queryKey: ["inventory"],
      queryFn: () => StoresService.readStoreInventory({
        id: Number(storeId)
      }), 
    })

  
    return (
      <Tbody>
        {stores.data.map((item) => ( // Update warehouse variable name
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
  
  function InventoryTable({storeId}: {storeId: string}) {
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
              <InventoryTableBody storeId={storeId}/>
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
    return (
      <Container maxW="full">
        <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
          Inventory Management for {params.storeId}
        </Heading>
        <Navbar type="Inventory"/>
        <InventoryTable storeId={params.storeId}/>
      </Container>
    )
  }
  
