import {  Heading, Text } from "@chakra-ui/react"

import DeleteConfirmation from "./DeleteConfirmation"

const DeleteAccount = () => {
  return (
    <Box maxW="7xl" mx="auto" px={6}>
      <Heading size="sm" py={4}>
        Delete Account
      </Heading>
      <Text>
        Permanently delete your data and everything associated with your
        account.
      </Text>
      <DeleteConfirmation />
    </Box>
  )
}
export default DeleteAccount
