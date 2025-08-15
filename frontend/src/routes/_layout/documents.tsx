"use client";

import {
  Checkbox,
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
import { Dispatch, SetStateAction, useState } from "react";

import { DocumentsService, DocumentPublic } from "@/client";
import { DocumentActionsMenu } from "@/components/Common/DocumentActionsMenu";
import AddDocument from "@/components/Documents/AddDocument";
import PendingDocuments from "@/components/Pending/PendingDocuments";
import GenerateQuestions from "@/components/Documents/GenerateQuestions";
import {
  PaginationDocuments,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx";

// ------------------- Constants & Schemas -------------------
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

// ------------------- Route -------------------
export const Route = createFileRoute("/_layout/documents")({
  component: Documents,
  validateSearch: (search) => documentsSearchSchema.parse(search),
});

// ------------------- Components -------------------
function EmptyDocuments() {
  return (
    <EmptyState.Root>
      <EmptyState.Content>
        <EmptyState.Indicator>
          <FiSearch />
        </EmptyState.Indicator>
        <VStack textAlign="center">
          <EmptyState.Title>You don't have any documents yet</EmptyState.Title>
          <EmptyState.Description>
            Add a new document to get started
          </EmptyState.Description>
        </VStack>
      </EmptyState.Content>
    </EmptyState.Root>
  );
}

function SelectAllCheckbox({
  selectedDocuments,
  documents,
  setSelectedDocuments,
}: {
  selectedDocuments: DocumentPublic[];
  documents: DocumentPublic[];
  setSelectedDocuments: Dispatch<SetStateAction<DocumentPublic[]>>;
}) {
  return (
    <Checkbox.Root
      size="sm"
      mt="0.5"
      aria-label="Select all rows"
      checked={selectedDocuments.length === documents.length}
      onCheckedChange={(changes) =>
        setSelectedDocuments(changes.checked ? [...documents] : [])
      }
    >
      <Checkbox.HiddenInput />
      <Checkbox.Control />
      <Checkbox.Label>Select All</Checkbox.Label>
    </Checkbox.Root>
  );
}

function DocumentRow({
  document,
  selectedDocuments,
  setSelectedDocuments,
  isPlaceholderData,
}: {
  document: DocumentPublic;
  selectedDocuments: DocumentPublic[];
  setSelectedDocuments: Dispatch<SetStateAction<DocumentPublic[]>>;
  isPlaceholderData: boolean;
}) {
  return (
    <Table.Row
      key={document.id}
      data-selected={selectedDocuments.includes(document) ? "" : undefined}
      opacity={isPlaceholderData ? 0.5 : 1}
    >
      <Table.Cell>
        <Checkbox.Root
          size="sm"
          mt="0.5"
          checked={selectedDocuments.includes(document)}
          onCheckedChange={(changes) =>
            setSelectedDocuments((prev: DocumentPublic[]) =>
              changes.checked
                ? [...prev, document]
                : prev.filter((d: DocumentPublic) => d.id !== document.id),
            )
          }
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
        </Checkbox.Root>
      </Table.Cell>

      <Table.Cell truncate maxW="sm">
        {document.id}
      </Table.Cell>
      <Table.Cell truncate maxW="sm">
        {document.filename || "N/A"}
      </Table.Cell>
      <Table.Cell
        color={!document.filename ? "gray" : "inherit"}
        truncate
        maxW="30%"
      >
        {document.content_type || "N/A"}
      </Table.Cell>
      <Table.Cell>
        <DocumentActionsMenu document={document} />
      </Table.Cell>
    </Table.Row>
  );
}

function DocumentsTable({
  selectedDocuments,
  setSelectedDocuments,
}: {
  selectedDocuments: DocumentPublic[];
  setSelectedDocuments: Dispatch<SetStateAction<DocumentPublic[]>>;
}) {
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

  if (isLoading) return <PendingDocuments />;
  if (documents.length === 0) return <EmptyDocuments />;

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="6">
              <SelectAllCheckbox
                selectedDocuments={selectedDocuments}
                documents={documents}
                setSelectedDocuments={setSelectedDocuments}
              />
            </Table.ColumnHeader>
            <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Name</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Content Type</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {documents.map((doc) => (
            <DocumentRow
              key={doc.id}
              document={doc}
              selectedDocuments={selectedDocuments}
              setSelectedDocuments={setSelectedDocuments}
              isPlaceholderData={isPlaceholderData}
            />
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

// ------------------- Page -------------------
function Documents() {
  const [selectedDocuments, setSelectedDocuments] = useState<DocumentPublic[]>(
    [],
  );

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Documents Management
      </Heading>
      <AddDocument />
      <GenerateQuestions selectedDocuments={selectedDocuments} />
      <DocumentsTable
        selectedDocuments={selectedDocuments}
        setSelectedDocuments={setSelectedDocuments}
      />
    </Container>
  );
}

export default Documents;
