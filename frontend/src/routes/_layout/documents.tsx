import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { FiSearch } from "react-icons/fi";
import { z } from "zod";

import { DocumentsService } from "@/client";
import { DocumentActionsMenu } from "@/components/Common/DocumentActionsMenu";
import AddDocument from "@/components/Documents/AddDocument";
import PendingDocuments from "@/components/Pending/PendingDocuments";
import {
  PaginationDocuments,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx";
import React from "react";

const documentsSearchSchema = z.object({
  page: z.number().catch(1),
});

const PER_PAGE = 5;

function getDocumentsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      DocumentsService.readDocuments({
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["documents", { page }],
  };
}

export const Route = createFileRoute("/_layout/documents")({
  component: Documents,
  validateSearch: (search) => documentsSearchSchema.parse(search),
});

function DocumentsTable() {
  const navigate = useNavigate({ from: Route.fullPath });
  const { page } = Route.useSearch();

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getDocumentsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  });

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    });

  const documents = data?.data.slice(0, PER_PAGE) ?? [];
  const count = data?.count ?? 0;

  if (isLoading) {
    return <PendingDocuments />;
  }

  if (documents.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>
              You don't have any documents yet
            </EmptyState.Title>
            <EmptyState.Description>
              Add a new document to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    );
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {documents?.map((document) => (
            <Table.Row key={document.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {document.id}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {document.title}
              </Table.Cell>
              <Table.Cell
                color={!document.description ? "gray" : "inherit"}
                truncate
                maxW="30%"
              >
                {document.description || "N/A"}
              </Table.Cell>
              <Table.Cell>
                <DocumentActionsMenu document={document} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationDocuments />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  );
}

function Documents() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Documents Management
      </Heading>
      <AddDocument />
      <DocumentsTable />
    </Container>
  );
}
