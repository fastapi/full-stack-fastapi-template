import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu"
import { Box, IconButton } from "@chakra-ui/react"

import { Link as RouteLink } from "@tanstack/react-router"
import { FaUserAstronaut } from "react-icons/fa"
import { FiLogOut, FiUser } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"

const UserMenu = () => {
  const { logout } = useAuth()

  const handleLogout = async () => {
    logout()
  }

  return (
    <>
      <Box>
        <MenuRoot>
          <MenuTrigger asChild>
            <IconButton
              m={2}
              aria-label="Options"
              rounded="full"
              data-testid="user-menu"
            >
              <FaUserAstronaut color="white" fontSize="18px" />
            </IconButton>
          </MenuTrigger>
          <MenuContent>
            <MenuItem value="profile" asChild>
              <RouteLink to="/settings">
                <FiUser fontSize="18px" />
                <Box flex="1">My profile</Box>
              </RouteLink>
            </MenuItem>
            <MenuItem
              value="logout"
              onClick={handleLogout}
              colorPalette="red"
              fontWeight="bold"
            >
              <FiLogOut fontSize="18px" />
              <Box flex="1">Log out</Box>
            </MenuItem>
          </MenuContent>
        </MenuRoot>
      </Box>
    </>
  )
}

export default UserMenu
