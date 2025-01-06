import { Box, IconButton, useDisclosure } from "@chakra-ui/react"

import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { ItemPublic, UserPublic } from "@/client"
import EditUser from "../Admin/EditUser"
import EditItem from "../Items/EditItem"
import Delete from "./DeleteAlert"

interface ActionsMenuProps {
  type: string
  value: ItemPublic | UserPublic
  disabled?: boolean
}

const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const deleteModal = useDisclosure()

  return (
    <>
      <MenuRoot>
        <MenuTrigger asChild>
          <IconButton size="sm" variant="ghost" disabled={disabled}>
            <BsThreeDotsVertical />
          </IconButton>
        </MenuTrigger>
        <MenuContent>
          <MenuItem value="edit" onClick={editUserModal.onOpen}>
            <FiEdit fontSize="16px" />
            <Box flex="1">Edit {type}</Box>
          </MenuItem>
          <MenuItem value="delete" onClick={deleteModal.onOpen} color="red">
            <FiTrash fontSize="16px" />
            <Box flex="1">Delete {type}</Box>
          </MenuItem>
          {type === "User" ? (
            <EditUser
              user={value as UserPublic}
              open={editUserModal.open}
              onClose={editUserModal.onClose}
            />
          ) : (
            <EditItem
              item={value as ItemPublic}
              open={editUserModal.open}
              onClose={editUserModal.onClose}
            />
          )}
          <Delete
            type={type}
            id={value.id}
            open={deleteModal.open}
            onClose={deleteModal.onClose}
          />
        </MenuContent>
      </MenuRoot>
    </>
  )
}

export default ActionsMenu
