import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { ItemPublic, UserPublic, PathInList } from "../../client"
import EditUser from "../Admin/EditUser"
import EditItem from "../Items/EditItem"
import Delete from "./DeleteAlert"

import { useNavigate } from "@tanstack/react-router"

interface ActionsMenuProps {
  type: string
  value: ItemPublic | UserPublic | PathInList
  disabled?: boolean
}

const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const editItemModal = useDisclosure()
  const deleteModal = useDisclosure()
  const navigate = useNavigate()

  const handleEdit = () => {
    if (type === "Path") {
      const path = value as PathInList
      navigate({ to: `/paths/${path.id}` })  // Match the route in /routes/paths/$pathId/index.tsx
    } else if (type === "Item") {
      editItemModal.onOpen()
    } else if (type === "User") {
      editUserModal.onOpen()
    }
  }

  return (
    <>
      <Menu>
        <MenuButton
          isDisabled={disabled}
          as={Button}
          rightIcon={<BsThreeDotsVertical />}
          variant="unstyled"
        />
        <MenuList>
          <MenuItem
            onClick={() => {
              console.log('Edit clicked, type:', type)
              console.log('Edit clicked, value:', value)
              handleEdit()
            }}
            icon={<FiEdit fontSize="16px" />}
          >
            Edit {type}
          </MenuItem>
          <MenuItem
            onClick={deleteModal.onOpen}
            icon={<FiTrash fontSize="16px" />}
            color="ui.danger"
          >
            Delete {type}
          </MenuItem>
        </MenuList>
        {type === "User" && (
          <EditUser
            user={value as UserPublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        )}
        {type === "Item" && (
          <EditItem
            item={value as ItemPublic}
            isOpen={editItemModal.isOpen}
            onClose={editItemModal.onClose}
          />
        )}
        <Delete
          type={type}
          id={value.id}
          isOpen={deleteModal.isOpen}
          onClose={deleteModal.onClose}
        />
      </Menu>
    </>
  )
}

export default ActionsMenu
