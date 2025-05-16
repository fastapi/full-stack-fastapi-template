import {
  Container,
  EmptyState,
  Flex,
  HStack,
  Heading,
  Table,
  VStack,
  Button,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiChevronDown, FiFilter, FiSearch } from "react-icons/fi"
import { z } from "zod"

import { TicketsService, type TicketStatus, type TicketCategory } from "@/client"
import { TicketActionsMenu } from "@/components/Common/TicketActionsMenu"
import AddTicket from "@/components/Tickets/AddTicket"
import PendingTickets from "@/components/Pending/PendingTickets"
import PriorityBadge from "@/components/Tickets/PriorityBadge"
import TicketStatusBadge from "@/components/Tickets/TicketStatusBadge"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"
import { 
  MenuContent,
  MenuRoot, 
  MenuTrigger,
  MenuItem
} from "@/components/ui/menu"
import { format } from "date-fns"

const ticketsSearchSchema = z.object({
  page: z.number().catch(1),
  status: z.string().optional().catch(undefined),
  category: z.string().optional().catch(undefined),
})

const PER_PAGE = 10

function getTicketsQueryOptions({ 
  page, 
  status, 
  category 
}: { 
  page: number, 
  status?: TicketStatus, 
  category?: TicketCategory 
}) {
  return {
    queryFn: () =>
      TicketsService.readTickets({ 
        skip: (page - 1) * PER_PAGE, 
        limit: PER_PAGE,
        status,
        category,
      }),
    queryKey: ["tickets", { page, status, category }],
  }
}

export const Route = createFileRoute("/_layout/tickets")({
  component: Tickets,
  validateSearch: (search) => ticketsSearchSchema.parse(search),
})

function TicketsTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page, status, category } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getTicketsQueryOptions({ page, status: status as TicketStatus, category: category as TicketCategory }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const setFilter = (type: "status" | "category", value?: string) => {
    navigate({
      search: (prev: { [key: string]: string }) => ({ 
        ...prev, 
        page: 1, 
        [type]: value 
      }),
    })
  }

  const tickets = data?.data ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingTickets />
  }

  if (tickets.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>No tickets found</EmptyState.Title>
            <EmptyState.Description>
              {status || category 
                ? "Try changing your filters" 
                : "Create a new ticket to get started"}
            </EmptyState.Description>
            {(status || category) && (
              <Button
                variant="outline"
                onClick={() => {
                  setFilter("status", undefined)
                  setFilter("category", undefined)
                }}
              >
                Clear filters
              </Button>
            )}
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <HStack mb={4} justifyContent="flex-end">
        <MenuRoot>
          <MenuTrigger asChild>
            <Button variant="outline">
              <HStack>
                <FiFilter />
                <span>Status: {status || "All"}</span>
                <FiChevronDown />
              </HStack>
            </Button>
          </MenuTrigger>
          <MenuContent>
            <MenuItem value="all" onClick={() => setFilter("status", undefined)}>
              All
            </MenuItem>
            <MenuItem value="open" onClick={() => setFilter("status", "Aberto")}>
              Open
            </MenuItem>
            <MenuItem value="in-progress" onClick={() => setFilter("status", "Em andamento")}>
              In Progress
            </MenuItem>
            <MenuItem value="closed" onClick={() => setFilter("status", "Encerrado")}>
              Closed
            </MenuItem>
          </MenuContent>
        </MenuRoot>

        <MenuRoot>
          <MenuTrigger asChild>
            <Button variant="outline">
              <HStack>
                <FiFilter />
                <span>Category: {category || "All"}</span>
                <FiChevronDown />
              </HStack>
            </Button>
          </MenuTrigger>
          <MenuContent>
            <MenuItem value="all-categories" onClick={() => setFilter("category", undefined)}>
              All
            </MenuItem>
            <MenuItem value="support" onClick={() => setFilter("category", "Suporte")}>
              Support
            </MenuItem>
            <MenuItem value="maintenance" onClick={() => setFilter("category", "Manutenção")}>
              Maintenance
            </MenuItem>
            <MenuItem value="question" onClick={() => setFilter("category", "Dúvida")}>
              Question
            </MenuItem>
          </MenuContent>
        </MenuRoot>
      </HStack>

      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>ID</Table.ColumnHeader>
            <Table.ColumnHeader>Title</Table.ColumnHeader>
            <Table.ColumnHeader>Category</Table.ColumnHeader>
            <Table.ColumnHeader>Priority</Table.ColumnHeader>
            <Table.ColumnHeader>Status</Table.ColumnHeader>
            <Table.ColumnHeader>Created</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {tickets?.map((ticket) => (
            <Table.Row key={ticket.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {ticket.id.substring(0, 8)}...
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {ticket.title}
              </Table.Cell>
              <Table.Cell>{ticket.category}</Table.Cell>
              <Table.Cell>
                <PriorityBadge priority={ticket.priority} />
              </Table.Cell>
              <Table.Cell>
                <TicketStatusBadge status={ticket.status || "Aberto"} />
              </Table.Cell>
              <Table.Cell>
                {format(new Date(ticket.created_at), "PP")}
              </Table.Cell>
              <Table.Cell>
                <TicketActionsMenu ticket={ticket} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          page={page}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Tickets() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Tickets Management
      </Heading>
      <AddTicket />
      <TicketsTable />
    </Container>
  )
}



