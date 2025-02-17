import { Skeleton, Table } from "@chakra-ui/react"

const PendingItems = () => (
  <Table.Root size={{ base: "sm", md: "md" }}>
    <Table.Header>
      <Table.Row>
        <Table.ColumnHeader>ID</Table.ColumnHeader>
        <Table.ColumnHeader>Title</Table.ColumnHeader>
        <Table.ColumnHeader>Description</Table.ColumnHeader>
        <Table.ColumnHeader>Actions</Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {[...Array(5)].map((_, index) => (
        <Table.Row key={index}>
          <Table.Cell>
            <Skeleton h="20px" w="100px" />
          </Table.Cell>
          <Table.Cell>
            <Skeleton h="20px" w="300px" />
          </Table.Cell>
          <Table.Cell>
            <Skeleton h="20px" w="300px" />
          </Table.Cell>
          <Table.Cell>
            <Skeleton h="20px" w="100px" />
          </Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table.Root>
)

export default PendingItems
