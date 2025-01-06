import { SkeletonText } from "@/components/ui/skeleton"
import { Badge, Box, Container, Flex, Heading, Table } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { type UserPublic, UsersService } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import ActionsMenu from "@/components/Common/ActionsMenu"
import EntityActionsBar from "@/components/Common/EntityActionsBar"
import { PaginationFooter } from "@/components/Common/PaginationFooter.tsx"

const usersSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  validateSearch: (search) => usersSearchSchema.parse(search),
})

const PER_PAGE = 5

function getUsersQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      UsersService.readUsers({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["users", { page }],
  }
}

function UsersTable() {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: number }) => ({ ...prev, page }),
    })

  const {
    data: users,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getUsersQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && users?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getUsersQueryOptions({ page: page + 1 }))
    }
    if (hasPreviousPage) {
      queryClient.prefetchQuery(getUsersQueryOptions({ page: page - 1 }))
    }
  }, [page, queryClient, hasNextPage, hasPreviousPage])

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader width="20%">Full name</Table.ColumnHeader>
            <Table.ColumnHeader width="50%">Email</Table.ColumnHeader>
            <Table.ColumnHeader width="10%">Role</Table.ColumnHeader>
            <Table.ColumnHeader width="10%">Status</Table.ColumnHeader>
            <Table.ColumnHeader width="10%">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        {isPending ? (
          <Table.Body>
            <Table.Row>
              {new Array(4).fill(null).map((_, index) => (
                <Table.Cell key={index}>
                  <SkeletonText lineClamp={1} paddingBlock="16px" />
                </Table.Cell>
              ))}
            </Table.Row>
          </Table.Body>
        ) : (
          <Table.Body>
            {users?.data.map((user) => (
              <Table.Row key={user.id}>
                <Table.Cell
                  color={!user.full_name ? "gray" : "inherit"}
                  truncate
                  maxWidth="150px"
                >
                  {user.full_name || "N/A"}
                  {currentUser?.id === user.id && (
                    <Badge ml="1" colorScheme="teal">
                      You
                    </Badge>
                  )}
                </Table.Cell>
                <Table.Cell truncate maxWidth="150px">
                  {user.email}
                </Table.Cell>
                <Table.Cell>
                  {user.is_superuser ? "Superuser" : "User"}
                </Table.Cell>
                <Table.Cell>
                  <Flex gap={2}>
                    <Box
                      w="2"
                      h="2"
                      borderRadius="50%"
                      bg={user.is_active ? "success" : "danger"}
                      alignSelf="center"
                    />
                    {user.is_active ? "Active" : "Inactive"}
                  </Flex>
                </Table.Cell>
                <Table.Cell>
                  <ActionsMenu
                    type="User"
                    value={user}
                    disabled={currentUser?.id === user.id}
                  />
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        )}
      </Table.Root>

      <PaginationFooter
        page={page}
        pageSize={PER_PAGE}
        count={users?.count || 0}
        setPage={setPage}
      />
    </>
  )
}

function Admin() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }}>
        Users Management
      </Heading>

      <EntityActionsBar type={"User"} addModalAs={AddUser} />
      <UsersTable />
    </Container>
  )
}
