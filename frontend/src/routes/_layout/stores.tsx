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
  import { createFileRoute } from "@tanstack/react-router"
  
  import { Suspense } from "react"
  import { ErrorBoundary } from "react-error-boundary"
  import { StoresService } from "../../client"
  import ActionsMenu from "../../components/Common/ActionsMenu"
  import Navbar from "../../components/Common/Navbar"
  
  export const Route = createFileRoute("/_layout/stores")({
    component: Stores,
  })
  
  function StoreTableBody() {
    const { data: stores } = useSuspenseQuery({
      queryKey: ["stores"],
      queryFn: () => StoresService.readStores({}), 
    })
  
    return (
      <Tbody>
        {stores.data.map((store) => ( // Update warehouse variable name
          <Tr key={store.id}>
            <Td>{store.title} <ActionsMenu type={"Store"} value={store} /> </Td> 
            <Td>
              <Link href={`/store/${store.id}/inventory`}>Go to Inventory</Link>
            </Td>
          </Tr>
        ))}
      </Tbody>
    )
  }
  
  function StoresTable() {
    return (
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Name</Th> 
              <Th>Action</Th>
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
              <StoreTableBody />
            </Suspense>
          </ErrorBoundary>
        </Table>
      </TableContainer>
    )
  }
  
  function Stores() { // Update function name to Store
    return (
      <Container maxW="full">
        <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
          Store Management
        </Heading>
  
        <Navbar type={"Stores"} />
        <StoresTable />
      </Container>
    )
  }
  