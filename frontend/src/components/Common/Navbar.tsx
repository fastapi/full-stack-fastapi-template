import {
  Box,
  Container,
  Flex,
  HStack,
  Image,
  Link,
  Text,
} from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"

import UserMenu from "./UserMenu"

export default function Navbar() {
  return (
    <Box
      as="nav"
      position="fixed"
      top={0}
      left={0}
      right={0}
      zIndex={1000}
      bg="white"
      borderBottom="1px"
      borderColor="gray.200"
      h="4rem"
      _dark={{
        bg: "gray.800",
        borderColor: "gray.700",
      }}
    >
      <Container h="100%" minW="100%">
        <Flex justify="space-between" align="center" h="100%">
          <HStack gap={4}>
            <RouterLink to="/">
              <HStack gap={3} _hover={{ opacity: 0.8 }}>
                <Text
                  fontSize="2xl"
                  fontWeight="bold"
                  color="#2F5249"
                  _hover={{ color: "#437057" }}
                  transition="color 0.2s"
                >
                  <Image src="/assets/images/logo.png" alt="Logo" w="160px" h="35px" />
                </Text>
              </HStack>
            </RouterLink>
          </HStack>

          <UserMenu />
        </Flex>
      </Container>
    </Box>
  )
}
