import { Box, Button, Flex, Text } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { FaUserAstronaut } from "react-icons/fa"
import { FiLogOut, FiUser } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"
import { MenuContent, MenuItem, MenuRoot, MenuTrigger } from "../ui/menu"

const UserMenu = () => {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    logout()
  }

  return (
    <>
      {/* Desktop */}
      <Flex>
        <MenuRoot>
          <MenuTrigger asChild p={2}>
            <Button 
              data-testid="user-menu" 
              bg="linear-gradient(135deg, #F59E0B, #FBBF24)"
              color="#1E3A8A"
              maxW="sm" 
              truncate
              fontWeight="600"
              _hover={{ bg: "linear-gradient(135deg, #D97706, #F59E0B)" }}
              boxShadow="0 2px 4px rgba(0,0,0,0.1)"
            >
              <FaUserAstronaut fontSize="18" />
              <Text>{user?.full_name || "User"}</Text>
            </Button>
          </MenuTrigger>

          <MenuContent bg="white" borderColor="#E2E8F0">
            <Link to="/settings">
              <MenuItem
                closeOnSelect
                value="user-settings"
                gap={2}
                py={2}
                style={{ cursor: "pointer" }}
                _hover={{ bg: "#F8FAFC" }}
              >
                <FiUser fontSize="18px" color="#1E40AF" />
                <Box flex="1" color="#1E293B">My Profile</Box>
              </MenuItem>
            </Link>

            <MenuItem
              value="logout"
              gap={2}
              py={2}
              onClick={handleLogout}
              style={{ cursor: "pointer" }}
              _hover={{ bg: "#FEF2F2" }}
            >
              <FiLogOut color="#EF4444" />
              <Text color="#1E293B">Log Out</Text>
            </MenuItem>
          </MenuContent>
        </MenuRoot>
      </Flex>
    </>
  )
}

export default UserMenu