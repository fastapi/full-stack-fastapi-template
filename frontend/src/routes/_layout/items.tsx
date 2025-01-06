import { SkeletonText } from "@/components/ui/skeleton"
import { Container, Heading, Table } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { ItemsService } from "@/client"
import ActionsMenu from "@/components/Common/ActionsMenu"
import EntityActionsBar from "@/components/Common/EntityActionsBar"
import { PaginationFooter } from "@/components/Common/PaginationFooter.tsx"
import AddItem from "@/components/Items/AddItem"

const itemsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/items")({
  component: Items,
  validateSearch: (search) => itemsSearchSchema.parse(search),
})

const PER_PAGE = 5

function getItemsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ItemsService.readItems({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["items", { page }],
  }
}

function ItemsTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: number }) => ({ ...prev, page }),
    })

  const {
    data: items,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getItemsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && items?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getItemsQueryOptions({ page: page + 1 }))
    }
    if (hasPreviousPage) {
      queryClient.prefetchQuery(getItemsQueryOptions({ page: page - 1 }))
    }
  }, [page, queryClient, hasNextPage, hasPreviousPage])

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>ID</Table.ColumnHeader>
            <Table.ColumnHeader>Title</Table.ColumnHeader>
            <Table.ColumnHeader>Description</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
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
            {items?.data.map((item) => (
              <Table.Row key={item.id} opacity={isPlaceholderData ? 0.5 : 1}>
                <Table.Cell>{item.id}</Table.Cell>
                <Table.Cell truncate maxWidth="150px">
                  {item.title}
                </Table.Cell>
                <Table.Cell
                  color={!item.description ? "gray" : "inherit"}
                  truncate
                  maxWidth="150px"
                >
                  {item.description || "N/A"}
                </Table.Cell>
                <Table.Cell>
                  <ActionsMenu type={"Item"} value={item} />
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        )}
      </Table.Root>

      <PaginationFooter
        page={page}
        pageSize={PER_PAGE}
        count={items?.count || 0}
        setPage={setPage}
      />
    </>
  )
}

function Items() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }}>
        Items Management
      </Heading>
      <EntityActionsBar type={"Item"} addModalAs={AddItem} />
      <ItemsTable />
    </Container>
  )
}
