import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Button, 
  IconButton,
  useDisclosure
} from "@chakra-ui/react"
import { Link, useRouterState } from "@tanstack/react-router"
import { useState } from "react"
import { FaBars } from "react-icons/fa"
import { FiLogOut } from "react-icons/fi"
import { useUser, useAuth } from '@clerk/clerk-react'
import { motion, AnimatePresence } from "framer-motion"
import {
  DrawerBackdrop,
  DrawerBody,
  DrawerCloseTrigger,
  DrawerContent,
  DrawerRoot,
} from "../ui/drawer"

interface SidebarItem {
  name: string
  path: string
  icon: string
  roles: string[]
  children?: SidebarItem[]
}

const sidebarItems: SidebarItem[] = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: "📊",
    roles: ["ceo", "manager", "supervisor", "hr", "support", "agent"],
  },
  {
    name: "Propiedades",
    path: "/properties",
    icon: "🏠",
    roles: ["ceo", "manager", "supervisor", "agent"],
    children: [
      { name: "Listado", path: "/properties", icon: "📋", roles: ["ceo", "manager", "supervisor", "agent"] },
      { name: "Agregar", path: "/properties/add", icon: "➕", roles: ["ceo", "manager", "supervisor", "agent"] },
      { name: "Favoritos", path: "/properties/favorites", icon: "❤️", roles: ["ceo", "manager", "supervisor", "agent"] },
    ]
  },
  {
    name: "Clientes",
    path: "/clients",
    icon: "👥",
    roles: ["ceo", "manager", "supervisor", "agent"],
  },
  {
    name: "Transacciones",
    path: "/transactions",
    icon: "💰",
    roles: ["ceo", "manager", "supervisor"],
  },
  {
    name: "Legal",
    path: "/legal",
    icon: "📋",
    roles: ["ceo", "manager", "supervisor"],
    children: [
      { name: "Documentos", path: "/legal/documents", icon: "📄", roles: ["ceo", "manager", "supervisor"] },
      { name: "Plantillas", path: "/legal/templates", icon: "📝", roles: ["ceo", "manager", "supervisor"] },
      { name: "Generador", path: "/legal/generator", icon: "⚡", roles: ["ceo", "manager", "supervisor"] },
    ]
  },
  {
    name: "Administración",
    path: "/admin",
    icon: "⚙️",
    roles: ["ceo", "manager"],
    children: [
      { name: "Usuarios", path: "/admin/users", icon: "👤", roles: ["ceo", "manager"] },
      { name: "Roles", path: "/admin/roles", icon: "🔐", roles: ["ceo"] },
      { name: "Configuración", path: "/admin/settings", icon: "🔧", roles: ["ceo"] },
    ]
  },
  {
    name: "Reportes",
    path: "/reports",
    icon: "📈",
    roles: ["ceo", "manager", "supervisor"],
  },
  {
    name: "Soporte",
    path: "/support",
    icon: "🎧",
    roles: ["support"],
  },
]

function RoleBasedAccess({ 
  allowedRoles, 
  children, 
  userRole 
}: { 
  allowedRoles: string[]
  children: React.ReactNode
  userRole: string
}) {
  if (!allowedRoles.includes(userRole)) {
    return null
  }
  return <>{children}</>
}

function SidebarItemComponent({ 
  item, 
  currentPath, 
  userRole,
  onItemClick
}: { 
  item: SidebarItem
  currentPath: string
  userRole: string
  onItemClick?: () => void
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const isActive = currentPath === item.path

  if (item.children) {
    return (
      <Box>
        <Button
          variant="ghost"
          justifyContent="flex-start"
          w="full"
          h="auto"
          p={3}
          bg={isActive ? "bg.muted" : "transparent"}
          color={isActive ? "text" : "text.muted"}
          _hover={{ bg: "bg.muted", color: "text" }}
          onClick={() => setIsExpanded(!isExpanded)}
          borderRadius="md"
        >
          <HStack spacing={3} w="full">
            <Text fontSize="lg">{item.icon}</Text>
            <Text flex={1} textAlign="left" fontWeight="medium">
              {item.name}
            </Text>
            <Text 
              fontSize="sm" 
              transform={isExpanded ? "rotate(90deg)" : "rotate(0deg)"}
              transition="transform 0.2s"
            >
              ▶
            </Text>
          </HStack>
        </Button>
        
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              style={{ overflow: "hidden" }}
            >
              <VStack spacing={1} mt={2} ml={6} align="stretch">
                {item.children
                  .filter(child => child.roles.includes(userRole))
                  .map((child) => (
                    <Link key={child.path} to={child.path} onClick={onItemClick}>
                      <Button
                        variant="ghost"
                        justifyContent="flex-start"
                        w="full"
                        h="auto"
                        p={2}
                        bg={currentPath === child.path ? "blue.600" : "transparent"}
                        color={currentPath === child.path ? "white" : "text.muted"}
                        _hover={{ bg: "bg.muted", color: "text" }}
                        borderRadius="md"
                        size="sm"
                      >
                        <HStack spacing={3}>
                          <Text fontSize="sm">{child.icon}</Text>
                          <Text fontWeight="medium">{child.name}</Text>
                        </HStack>
                      </Button>
                    </Link>
                  ))}
              </VStack>
            </motion.div>
          )}
        </AnimatePresence>
      </Box>
    )
  }

  return (
    <Link to={item.path} onClick={onItemClick}>
      <Button
        variant="ghost"
        justifyContent="flex-start"
        w="full"
        h="auto"
        p={3}
        bg={isActive ? "blue.600" : "transparent"}
        color={isActive ? "white" : "text.muted"}
        _hover={{ bg: isActive ? "blue.700" : "bg.muted", color: "text" }}
        borderRadius="md"
      >
        <HStack spacing={3}>
          <Text fontSize="lg">{item.icon}</Text>
          <Text fontWeight="medium">{item.name}</Text>
        </HStack>
      </Button>
    </Link>
  )
}

const Sidebar = () => {
  const { user } = useUser()
  const { signOut } = useAuth()
  const routerState = useRouterState()
  const currentPath = routerState.location.pathname
  const userRole = user?.publicMetadata?.role as string || "user"
  const { isOpen, onOpen, onClose } = useDisclosure()

  return (
    <>
      {/* Mobile Menu Button */}
      <IconButton
        icon={<FaBars />}
        variant="ghost"
        color="text"
        display={{ base: "flex", md: "none" }}
        aria-label="Open Menu"
        position="fixed"
        top={4}
        left={4}
        zIndex={1001}
        onClick={onOpen}
        bg="bg.surface"
        _hover={{ bg: "bg.muted" }}
      />

      {/* Mobile Drawer */}
      <DrawerRoot isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerBackdrop />
        <DrawerContent bg="bg.surface" borderColor="border">
          <DrawerCloseTrigger />
          <DrawerBody p={4}>
            <VStack spacing={2} align="stretch">
              <Text fontSize="lg" fontWeight="bold" color="text" mb={4}>
                GENIUS INDUSTRIES
              </Text>
              
              {sidebarItems.map((item) => (
                <RoleBasedAccess key={item.path} allowedRoles={item.roles} userRole={userRole}>
                  <SidebarItemComponent 
                    item={item} 
                    currentPath={currentPath}
                    userRole={userRole}
                    onItemClick={onClose}
                  />
                </RoleBasedAccess>
              ))}
              
              <Button
                variant="ghost"
                justifyContent="flex-start"
                w="full"
                h="auto"
                p={3}
                color="red.400"
                _hover={{ bg: "red.900", color: "red.300" }}
                onClick={() => signOut()}
                borderRadius="md"
                mt={4}
              >
                <HStack spacing={3}>
                  <FiLogOut />
                  <Text fontWeight="medium">Cerrar Sesión</Text>
                </HStack>
              </Button>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </DrawerRoot>

      {/* Desktop Sidebar */}
      <Box
        pos="fixed"
        top={0}
        left={0}
        h="100vh"
        w="280px"
        bg="bg.surface"
        borderRight="1px solid"
        borderColor="border"
        display={{ base: "none", md: "block" }}
        overflowY="auto"
        pt={20}
      >
        <VStack spacing={2} align="stretch" p={4}>
          {sidebarItems.map((item) => (
            <RoleBasedAccess key={item.path} allowedRoles={item.roles} userRole={userRole}>
              <SidebarItemComponent 
                item={item} 
                currentPath={currentPath}
                userRole={userRole}
              />
            </RoleBasedAccess>
          ))}
          
          <Button
            variant="ghost"
            justifyContent="flex-start"
            w="full"
            h="auto"
            p={3}
            color="red.400"
            _hover={{ bg: "red.900", color: "red.300" }}
            onClick={() => signOut()}
            borderRadius="md"
            mt={4}
          >
            <HStack spacing={3}>
              <FiLogOut />
              <Text fontWeight="medium">Cerrar Sesión</Text>
            </HStack>
          </Button>
        </VStack>
      </Box>
    </>
  )
}

export default Sidebar 