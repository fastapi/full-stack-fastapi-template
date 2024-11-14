// **Admin User Management Page (admin.tsx)**
// This file sets up the admin user management page under the '/_layout/admin' route.
// It includes a paginated list of users, with options to view user details, 
// update user status, and manage actions (like edit or delete).
// The page utilizes React Query for data fetching, Zod for validation, 
// and Chakra UI for the UI components such as tables and buttons. 
// The page is part of a larger admin panel for managing users.

import {
  Badge,
  Box,
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
} from "@chakra-ui/react" // Chakra UI components for UI structure
import { useQuery, useQueryClient } from "@tanstack/react-query" // React Query hooks for fetching data
import { createFileRoute, useNavigate } from "@tanstack/react-router" // Router hooks for route management
import { useEffect } from "react" // React's effect hook for side-effects
import { z } from "zod" // Zod for schema validation

// Importing user API and UI components
import { type UserPublic, UsersService } from "../../client" // UsersService handles the API for fetching users
import AddUser from "../../components/Admin/AddUser" // AddUser component for adding new users
import ActionsMenu from "../../components/Common/ActionsMenu" // Menu for user actions (edit, delete)
import Navbar from "../../components/Common/Navbar" // Navbar for the admin layout

// Zod schema to validate the page number query parameter in the URL
const usersSearchSchema = z.object({
  page: z.number().catch(1), // Default to page 1 if not provided
})

// Define the route for the admin section under the "/_layout/admin" path
export const Route = createFileRoute("/_layout/admin")({
  component: Admin, // The component to render for this route
  validateSearch: (search) => usersSearchSchema.parse(search), // Validating search query parameters
})

const PER_PAGE = 5 // Number of users per page for pagination

// Function to build query options for fetching users
function getUsersQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      UsersService.readUsers({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }), // Fetch users with pagination
    queryKey: ["users", { page }], // Query key for caching and managing requests
  }
}

// Component to display the users table with pagination
function UsersTable() {
  const queryClient = useQueryClient() // React Query's client for managing data caching
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"]) // Get the current user data
  const { page } = Route.useSearch() // Get the current page from the route's search parameters
  const navigate = useNavigate({ from: Route.fullPath }) // Hook to navigate within the app
  const setPage = (page: number) =>
    navigate({ search: (prev) => ({ ...prev, page }) }) // Navigate to the next/previous page with updated query

  // Fetching the user data using React Query
  const {
    data: users, // The fetched user data
    isPending, // Whether the data is still being fetched
    isPlaceholderData, // Whether the data is just a placeholder while fetching
  } = useQuery({
    ...getUsersQueryOptions({ page }), // The query options
    placeholderData: (prevData) => prevData, // Placeholder data while the query is in progress
  })

  // Flags for checking pagination availability
  const hasNextPage = !isPlaceholderData && users?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  // Prefetch the next page if available (for smoother user experience)
  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getUsersQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th width="20%">Full name</Th>
              <Th width="50%">Email</Th>
              <Th width="10%">Role</Th>
              <Th width="10%">Status</Th>
              <Th width="10%">Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            // Show a loading skeleton while the data is being fetched
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            // Show the user data once it's loaded
            <Tbody>
              {users?.data.map((user) => (
                <Tr key={user.id}>
                  <Td
                    color={!user.full_name ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {user.full_name || "N/A"}
                    {currentUser?.id === user.id && (
                      // If this is the current user, display a "You" badge
                      <Badge ml="1" colorScheme="teal">
                        You
                      </Badge>
                    )}
                  </Td>
                  <Td isTruncated maxWidth="150px">{user.email}</Td>
                  <Td>{user.is_superuser ? "Superuser" : "User"}</Td>
                  <Td>
                    <Flex gap={2}>
                      <Box
                        w="2"
                        h="2"
                        borderRadius="50%"
                        bg={user.is_active ? "ui.success" : "ui.danger"}
                        alignSelf="center"
                      />
                      {user.is_active ? "Active" : "Inactive"}
                    </Flex>
                  </Td>
                  <Td>
                    <ActionsMenu
                      type="User"
                      value={user}
                      disabled={currentUser?.id === user.id ? true : false}
                    />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      {/* Pagination controls */}
      <Flex
        gap={4}
        alignItems="center"
        mt={4}
        direction="row"
        justifyContent="flex-end"
      >
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

// Admin component renders the admin page with user management tools
function Admin() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Users Management
      </Heading>
      {/* Navbar and Add User button */}
      <Navbar type={"User"} addModalAs={AddUser} />
      <UsersTable />
    </Container>
  )
}