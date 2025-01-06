import type { ComponentType, ElementType } from "react"

import { Button, Flex, useDisclosure } from "@chakra-ui/react"
import { FaPlus } from "react-icons/fa"

interface NavbarProps {
  type: string
  addModalAs: ComponentType | ElementType
}

const EntityActionsBar = ({ type, addModalAs }: NavbarProps) => {
  const addModal = useDisclosure()

  const AddModal = addModalAs
  return (
    <Flex py={8} gap={4}>
      {/* TODO: Complete search functionality */}
      {/* <InputGroup w={{ base: '100%', md: 'auto' }}>
                    <InputLeftElement pointerEvents='none'>
                        <Icon colorPalette='gray' ><FaSearch/></Icon>
                    </InputLeftElement>
                    <Input type='text' placeholder='Search' fontSize={{ base: 'sm', md: 'inherit' }} borderRadius='8px' />
                </InputGroup> */}
      <Button
        gap={1}
        fontSize={{ base: "sm", md: "inherit" }}
        onClick={addModal.onOpen}
      >
        <FaPlus /> Add {type}
      </Button>
      <AddModal open={addModal.open} onClose={addModal.onClose} />
    </Flex>
  )
}

export default EntityActionsBar
