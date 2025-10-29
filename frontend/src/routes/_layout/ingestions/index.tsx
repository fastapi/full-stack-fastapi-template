import { Badge, Container, Flex, Heading, Table } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { z } from "zod"

import { type IngestionPublic, IngestionsService } from "@/client"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination"

const ingestionsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/ingestions/")({
  component: IngestionsListPage,
  validateSearch: (search) => ingestionsSearchSchema.parse(search),
})

const PER_PAGE = 20

function getIngestionsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      IngestionsService.readIngestions({
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["ingestions", { page }],
  }
}

function IngestionsListPage() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const [currentPage, setCurrentPage] = useState(page)

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getIngestionsQueryOptions({ page: currentPage }),
    placeholderData: (prevData) => prevData,
  })

  const handlePageChange = ({ page }: { page: number }) => {
    setCurrentPage(page)
    navigate({ search: { page } })

    // Prefetch next page
    if (!isPlaceholderData && data?.count) {
      const hasNextPage = page * PER_PAGE < data.count
      if (hasNextPage) {
        queryClient.prefetchQuery(getIngestionsQueryOptions({ page: page + 1 }))
      }
    }
  }

  const handleRowClick = (ingestionId: string) => {
    // Navigate to review page (not yet implemented)
    window.location.href = `/ingestions/${ingestionId}/review`
  }

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(2)} MB`
  }

  const formatDate = (date: string): string => {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      UPLOADED: "blue",
      DRAFT: "gray",
      IN_REVIEW: "orange",
      APPROVED: "green",
      REJECTED: "red",
    }
    return colors[status] || "gray"
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Ingestions
      </Heading>

      {isLoading ? (
        <p>Loading...</p>
      ) : !data || data.data.length === 0 ? (
        <Flex direction="column" alignItems="center" py={12}>
          <Heading size="md" mb={4}>
            No worksheets uploaded yet
          </Heading>
          <p>Upload your first PDF worksheet to get started.</p>
        </Flex>
      ) : (
        <>
          <Table.Root size={{ base: "sm", md: "md" }} mt={8}>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Filename</Table.ColumnHeader>
                <Table.ColumnHeader>Upload Date</Table.ColumnHeader>
                <Table.ColumnHeader>Pages</Table.ColumnHeader>
                <Table.ColumnHeader>Status</Table.ColumnHeader>
                <Table.ColumnHeader>Size</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {data.data.map((ingestion: IngestionPublic) => (
                <Table.Row
                  key={ingestion.id}
                  onClick={() => ingestion.id && handleRowClick(ingestion.id)}
                  style={{ cursor: "pointer" }}
                  _hover={{ bg: "gray.50" }}
                >
                  <Table.Cell>{ingestion.filename}</Table.Cell>
                  <Table.Cell>{formatDate(ingestion.uploaded_at)}</Table.Cell>
                  <Table.Cell>{ingestion.page_count || "N/A"}</Table.Cell>
                  <Table.Cell>
                    <Badge
                      colorPalette={getStatusColor(
                        ingestion.status || "UPLOADED",
                      )}
                    >
                      {ingestion.status || "UPLOADED"}
                    </Badge>
                  </Table.Cell>
                  <Table.Cell>{formatFileSize(ingestion.file_size)}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>

          {data.count > PER_PAGE && (
            <Flex
              gap={4}
              alignItems="center"
              justifyContent="space-between"
              mt={8}
            >
              <span>
                Showing {(currentPage - 1) * PER_PAGE + 1} to{" "}
                {Math.min(currentPage * PER_PAGE, data.count)} of {data.count}{" "}
                ingestions
              </span>
              <PaginationRoot
                count={data.count}
                pageSize={PER_PAGE}
                page={currentPage}
                onPageChange={handlePageChange}
              >
                <Flex gap={4}>
                  <PaginationPrevTrigger />
                  <PaginationItems />
                  <PaginationNextTrigger />
                </Flex>
              </PaginationRoot>
            </Flex>
          )}
        </>
      )}
    </Container>
  )
}
