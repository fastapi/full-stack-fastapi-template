import { Button, Flex, Icon, useDisclosure } from "@chakra-ui/react"
import { FaPlus } from "react-icons/fa"

import AddUser from "../Admin/AddUser"
import AddItem from "../Items/AddItem"
import AddStore from "../Stores/AddStore"
import AddStoreInventory from "./Inventory/AddInventoryItems"
import useAuth from "../../hooks/useAuth"

interface NavbarProps {
  type: string
}

const Navbar = ({ type }: NavbarProps) => {
  const addUserModal = useDisclosure()
  const addItemModal = useDisclosure()
  const addStoreModal = useDisclosure()
  const addStoreInventoryModal = useDisclosure()

  const { isAdmin } = useAuth()

  const getModal = (type: string) => {
    switch (type) {
      case "User":
        addUserModal.onOpen();
        break;
      case "Items":
        addItemModal.onOpen();
        break;
      case "Stores":
        addStoreModal.onOpen();
        break;
      case "Inventory":
        addStoreInventoryModal.onOpen();
        break;
    }
  };

  return (
    <>
      <Flex py={8} gap={4}>
        {/* TODO: Complete search functionality */}
        {/* <InputGroup w={{ base: '100%', md: 'auto' }}>
                    <InputLeftElement pointerEvents='none'>
                        <Icon as={FaSearch} color='ui.dim' />
                    </InputLeftElement>
                    <Input type='text' placeholder='Search' fontSize={{ base: 'sm', md: 'inherit' }} borderRadius='8px' />
                </InputGroup> */}
        {isAdmin && <Button
          variant="primary"
          gap={1}
          fontSize={{ base: "sm", md: "inherit" }}
          onClick={() => getModal(type)}
        >
          <Icon as={FaPlus} /> Add {type}
        </Button>}
        <AddUser isOpen={addUserModal.isOpen} onClose={addUserModal.onClose} />
        <AddItem isOpen={addItemModal.isOpen} onClose={addItemModal.onClose} />
        <AddStore isOpen={addStoreModal.isOpen} onClose={addStoreModal.onClose} />
        <AddStoreInventory isOpen={addStoreInventoryModal.isOpen} onClose={addStoreInventoryModal.onClose} />
     
      </Flex>
    </>
  )
}

export default Navbar
