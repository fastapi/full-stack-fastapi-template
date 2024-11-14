// **Items Management Page (items.tsx)**
// This file defines the route and page for managing items in the application. 
// It utilizes Chakra UI for styling, TanStack React Query for data fetching, and React Router for navigation.
// The page provides an interface to list items, paginate through them, and perform actions on them, such as editing or deleting.

import {
  Button,
  Container,
  Flex,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react" // Chakra UI components for layout, styling, and table rendering
import { useQuery, useQueryClient } from "@tanstack/react-query" // TanStack React Query hooks for data fetching and caching
import { createFileRoute, useNavigate } from "@tanstack/react-router" // TanStack React Router for route management
import { useEffect } from "react"
import { z } from "zod" // Zod for schema validation

import { ItemsService } from "../../client" // Service to interact with the backend for fetching items
import ActionsMenu from "../../components/Common/ActionsMenu" // Action menu component for individual items
import Navbar from "../../components/Common/Navbar" // Navbar component for page navigation
import AddItem from "../../components/Items/AddItem" // Modal for adding new items

// Define schema for validating search parameters (page number)
const itemsSearchSchema = z.object({
  page: z.number().catch(1), // Default to page 1 if no page is provided
})

// Route setup for the "/_layout/items" path
export const Route = createFileRoute("/_layout/items")({
  component: Items, // The component to render for this route
  validateSearch: (search) => itemsSearchSchema.parse(search), // Validate search params
})

const PER_PAGE = 5 // Number of items to display per page

// Function to generate query options for fetching items data
function getItemsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ItemsService.readItems({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }), // Fetch items for the given page
    queryKey: ["items", { page }], // Unique query key for caching and refetching
  }
}

// ItemsTable component responsible for rendering the table of items
function ItemsTable() {
  const queryClient = useQueryClient() // Access query cache for prefetching and caching data
  const { page } = Route.useSearch() // Get the current page from the search parameters
  const navigate = useNavigate({ from: Route.fullPath }) // Navigation hook to change search params
  const setPage = (page: number) =>
    navigate({ search: (prev) => ({ ...prev, page }) }) // Function to update the current page in the URL

  // Fetch items data using React Query
  const {
    data: items,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getItemsQueryOptions({ page }),
    placeholderData: (prevData) => prevData, // Use previous data while fetching new data
  })

  // Pagination logic
  const hasNextPage = !isPlaceholderData && items?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  // Prefetch next page of items if there's a next page
  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getItemsQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      {/* Render the items table */}
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
          {isPending ? (
            <Tbody>
              <Tr>
                {/* Render skeleton loaders while data is pending */}
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {/* Render fetched items */}
              {items?.data.map((item) => (
                <Tr key={item.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{item.id}</Td>
                  <Td isTruncated maxWidth="150px">{item.title}</Td>
                  <Td color={!item.description ? "ui.dim" : "inherit"} isTruncated maxWidth="150px">
                    {item.description || "N/A"}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Item"} value={item} /> {/* Actions menu for each item */}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>

      {/* Pagination controls */}
      <Flex gap={4} alignItems="center" mt={4} direction="row" justifyContent="flex-end">
        <Button onClick={() => setPage(page - 1)} isDisabled={!hasPreviousPage}>
          Previous
        </Button>
        <span>Page {page}</span>
        <Button isDisabled={!hasNextPage} onClick={() => setPage(page + 1)}>
          Next
        </Button>
      </Flex>
    </>
  )
}

// Main Items component rendering the page layout
function Items() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Items Management
      </Heading>

      {/* Navbar with AddItem modal for adding new items */}
      <Navbar type={"Item"} addModalAs={AddItem} />
      <ItemsTable /> {/* Display the list of items */}
    </Container>
  )
}