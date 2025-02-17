import {
    Skeleton,
    Table
} from "@chakra-ui/react"
  
  const PendingUsers = () => (
    <Table.Root size={{ base: "sm", md: "md" }}>
      <Table.Header>
        <Table.Row>
        <Table.ColumnHeader w="200px">Full name</Table.ColumnHeader>
            <Table.ColumnHeader w="300px">Email</Table.ColumnHeader>
            <Table.ColumnHeader w="200px">Role</Table.ColumnHeader>
            <Table.ColumnHeader w="200px">Status</Table.ColumnHeader>
            <Table.ColumnHeader w="100px">Actions</Table.ColumnHeader>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {[...Array(5)].map((_, index) => (
          <Table.Row key={index}>
            <Table.Cell>
              <Skeleton h="20px" w="200px" />
            </Table.Cell>
            <Table.Cell>
              <Skeleton h="20px" w="300px" />
            </Table.Cell>
            <Table.Cell>
              <Skeleton h="20px" w="200px" />
            </Table.Cell>
            <Table.Cell>
              <Skeleton h="20px" w="200px" />
            </Table.Cell>
            <Table.Cell>
              <Skeleton h="20px" w="100px" />
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  )
  
  export default PendingUsers
  