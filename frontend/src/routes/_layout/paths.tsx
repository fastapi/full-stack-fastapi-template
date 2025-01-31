import React from "react"
import {
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { PathsService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import { PaginationFooter } from "../../components/Common/PaginationFooter"

const pathsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute('/_layout/paths')({
  component: Paths,
  validateSearch: (search) => pathsSearchSchema.parse(search),
})

const PER_PAGE = 5

function getPathsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      PathsService.listPaths({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["paths", { page }],
  }
}

function PathsTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ 
      to: "/paths",
      search: (prev) => ({ ...prev, page }) 
    })

  const {
    data: paths,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getPathsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && paths?.data?.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getPathsQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Title</Th>
              <Th>Summary</Th>
              <Th>Steps</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
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
            <Tbody>
              {paths?.data?.map((path) => (
                <Tr key={path.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td isTruncated maxWidth="200px">
                    {path.title}
                  </Td>
                  <Td
                    color={!path.path_summary ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="300px"
                  >
                    {path.path_summary || "N/A"}
                  </Td>
                  <Td>{path.steps?.length || 0}</Td>
                  <Td>
                    <ActionsMenu
                      type="Path"
                      value={path}
                      onEdit={() => navigate({ to: `/paths/${path.id}/edit` })}
                      onView={() => navigate({ to: `/paths/${path.id}` })}
                    />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  )
}

function Paths() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Learning Paths
      </Heading>

      <Navbar type="Path" addModalAs={() => null} />
      <PathsTable />
    </Container>
  )
}
