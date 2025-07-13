import { Box, VStack } from "@chakra-ui/react"
import SidebarItems from "./SidebarItems"

export default function Sidebar() {
  return (
    <Box
      as="aside"
      position="fixed"
      top="4rem"
      left={0}
      h="calc(100vh - 4rem)"
      w="16rem"
      bg="white"
      borderRight="1px"
      borderColor="gray.200"
      display={{ base: "none", md: "block" }}
      _dark={{
        bg: "gray.800",
        borderColor: "gray.700",
      }}
    >
      <VStack align="stretch" h="100%" py={4} gap={2}>
        <SidebarItems />
      </VStack>
    </Box>
  )
}
