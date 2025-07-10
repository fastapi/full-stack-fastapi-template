import { useState } from 'react'
import { Box, VStack, HStack, Heading, Text, Button, Progress, Icon, SimpleGrid, Badge } from '@chakra-ui/react'
import { FiFileText, FiEdit3, FiDownload, FiPlus, FiClock, FiCheckCircle, FiUser, FiCalendar } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'

interface Document {
  id: string
  name: string
  type: string
  status: 'draft' | 'active' | 'expired'
  created_date: string
  last_modified: string
  client?: string
  property?: string
}

interface Template {
  id: string
  name: string
  category: string
  usage_count: number
}

export const LegalDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview')
  
  // Datos de ejemplo
  const recentDocuments: Document[] = [
    {
      id: '1',
      name: 'Contrato de Compraventa - Casa Zona Norte',
      type: 'sale_contract',
      status: 'active',
      created_date: '2024-01-15',
      last_modified: '2024-01-16',
      client: 'María González',
      property: 'Casa Zona Norte'
    },
    {
      id: '2',
      name: 'Contrato de Arrendamiento - Apto Centro',
      type: 'rental_contract',
      status: 'draft',
      created_date: '2024-01-14',
      last_modified: '2024-01-14',
      client: 'Carlos Ruiz',
      property: 'Apartamento Centro'
    }
  ]

  const templates: Template[] = [
    { id: '1', name: 'Contrato de Compraventa', category: 'Ventas', usage_count: 45 },
    { id: '2', name: 'Contrato de Arrendamiento', category: 'Arriendos', usage_count: 32 },
    { id: '3', name: 'Promesa de Compraventa', category: 'Ventas', usage_count: 18 }
  ]

  const stats = {
    total_documents: 156,
    active_contracts: 89,
    pending_reviews: 12,
    templates_available: 8
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green'
      case 'draft': return 'yellow'
      case 'expired': return 'red'
      default: return 'gray'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Activo'
      case 'draft': return 'Borrador'
      case 'expired': return 'Expirado'
      default: return 'Desconocido'
    }
  }

  const renderOverview = () => (
    <VStack spacing={6} align="stretch">
      {/* Stats Cards */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
        <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
          <HStack justify="space-between" mb={2}>
            <Icon as={FiFileText} w={8} h={8} color="blue.400" />
            <Text color="blue.400" fontSize="2xl" fontWeight="bold">
              {stats.total_documents}
            </Text>
          </HStack>
          <Text color="text" fontSize="sm" fontWeight="medium">Total Documentos</Text>
          <Text color="text.muted" fontSize="xs">Último mes</Text>
        </Box>

        <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
          <HStack justify="space-between" mb={2}>
            <Icon as={FiCheckCircle} w={8} h={8} color="green.400" />
            <Text color="green.400" fontSize="2xl" fontWeight="bold">
              {stats.active_contracts}
            </Text>
          </HStack>
          <Text color="text" fontSize="sm" fontWeight="medium">Contratos Activos</Text>
          <Text color="text.muted" fontSize="xs">En vigencia</Text>
        </Box>

        <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
          <HStack justify="space-between" mb={2}>
            <Icon as={FiClock} w={8} h={8} color="orange.400" />
            <Text color="orange.400" fontSize="2xl" fontWeight="bold">
              {stats.pending_reviews}
            </Text>
          </HStack>
          <Text color="text" fontSize="sm" fontWeight="medium">Pendientes Revisión</Text>
          <Text color="text.muted" fontSize="xs">Requieren atención</Text>
        </Box>

        <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
          <HStack justify="space-between" mb={2}>
            <Icon as={FiEdit3} w={8} h={8} color="purple.400" />
            <Text color="purple.400" fontSize="2xl" fontWeight="bold">
              {stats.templates_available}
            </Text>
          </HStack>
          <Text color="text" fontSize="sm" fontWeight="medium">Plantillas Disponibles</Text>
          <Text color="text.muted" fontSize="xs">Listas para usar</Text>
        </Box>
      </SimpleGrid>

      {/* Recent Documents */}
      <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
        <HStack justify="space-between" mb={4}>
          <Heading size="md" color="text">Documentos Recientes</Heading>
          <Button size="sm" colorScheme="blue" leftIcon={<FiPlus />}>
            Nuevo Documento
          </Button>
        </HStack>

        <VStack spacing={3} align="stretch">
          {recentDocuments.map((doc) => (
            <Box
              key={doc.id}
              p={4}
              bg="bg.muted"
              borderRadius="md"
              border="1px"
              borderColor="border.muted"
            >
              <HStack justify="space-between" mb={2}>
                <VStack align="start" spacing={1} flex={1}>
                  <HStack>
                    <Icon as={FiFileText} w={4} h={4} color="text.muted" />
                    <Text fontWeight="semibold" color="text" fontSize="sm">
                      {doc.name}
                    </Text>
                  </HStack>
                  <HStack spacing={4} fontSize="xs" color="text.muted">
                    <HStack>
                      <Icon as={FiUser} w={3} h={3} />
                      <Text>{doc.client}</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiCalendar} w={3} h={3} />
                      <Text>{new Date(doc.created_date).toLocaleDateString()}</Text>
                    </HStack>
                  </HStack>
                </VStack>
                <VStack spacing={2}>
                  <Badge colorScheme={getStatusColor(doc.status)} size="sm">
                    {getStatusLabel(doc.status)}
                  </Badge>
                  <HStack spacing={1}>
                    <Button size="xs" variant="outline" borderColor="border" color="text">
                      <Icon as={FiEdit3} w={3} h={3} />
                    </Button>
                    <Button size="xs" variant="outline" borderColor="border" color="text">
                      <Icon as={FiDownload} w={3} h={3} />
                    </Button>
                  </HStack>
                </VStack>
              </HStack>
            </Box>
          ))}
        </VStack>
      </Box>

      {/* Templates */}
      <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
        <Heading size="md" mb={4} color="text">Plantillas Más Utilizadas</Heading>
        <VStack spacing={3}>
          {templates.map((template) => (
            <HStack key={template.id} justify="space-between" w="full" p={3} bg="bg.muted" borderRadius="md">
              <VStack align="start" spacing={1}>
                <Text fontWeight="medium" color="text">{template.name}</Text>
                <Text fontSize="sm" color="text.muted">{template.category}</Text>
              </VStack>
              <VStack align="end" spacing={1}>
                <Text fontSize="sm" color="text">{template.usage_count} usos</Text>
                <Button size="xs" colorScheme="blue">Usar</Button>
              </VStack>
            </HStack>
          ))}
        </VStack>
      </Box>
    </VStack>
  )

  return (
    <RoleDashboard
      title="Sistema Legal"
      description="Gestión de documentos y contratos legales"
    >
      {renderOverview()}
    </RoleDashboard>
  )
} 
