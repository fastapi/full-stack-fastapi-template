import { Box, Flex, Heading, useBreakpointValue } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { FiCamera } from "react-icons/fi"

import UserMenu from "./UserMenu"

function Navbar() {
  const display = useBreakpointValue({ base: "none", md: "flex" })

  return (
    <Flex
      display={display}
      justify="space-between"
      position="sticky"
      align="center"
      bg="linear-gradient(135deg, #1E3A8A, #2563EB)"
      w="100%"
      top={0}
      p={4}
      borderBottom="1px solid #1E40AF"
      boxShadow="0 2px 4px rgba(0,0,0,0.1)"
    >
      <Link to="/">
        <Flex align="center" gap={3}>
          <Box 
            w="40px" 
            h="40px" 
            bg="linear-gradient(135deg, #F59E0B, #FBBF24)" 
            borderRadius="md"
            display="flex"
            alignItems="center"
            justifyContent="center"
            boxShadow="0 2px 4px rgba(0,0,0,0.2)"
          >
            <FiCamera size={24} color="#1E3A8A" />
          </Box>
          <Heading
            size="2xl"
            fontWeight="700"
            letterSpacing="wide"
            color="#F59E0B"
            fontFamily="'Poppins', sans-serif"
            _hover={{ opacity: 0.9 }}
          >
            MOSAIC
          </Heading>
        </Flex>
      </Link>
      <Flex gap={2} alignItems="center">
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar