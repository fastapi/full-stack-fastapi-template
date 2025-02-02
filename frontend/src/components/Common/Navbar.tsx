import type { ComponentType, ElementType } from "react"

import { Button, Flex, Icon } from "@chakra-ui/react"
import { FaPlus } from "react-icons/fa"
import { useNavigate } from "@tanstack/react-router"

interface NavbarProps {
  type: string
  addModalAs: ComponentType | ElementType
}

const Navbar = ({ type, addModalAs: AddButton }: NavbarProps) => {
  return (
    <Flex py={8} gap={4}>
      {/* TODO: Complete search functionality */}
      {/* <InputGroup w={{ base: '100%', md: 'auto' }}>
                <InputLeftElement pointerEvents='none'>
                    <Icon as={FaSearch} color='ui.dim' />
                </InputLeftElement>
                <Input type='text' placeholder='Search' fontSize={{ base: 'sm', md: 'inherit' }} borderRadius='8px' />
            </InputGroup> */}
      <AddButton />
    </Flex>
  )
}

export default Navbar
