import { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Select,
  Input,
  Textarea,
  FormControl,
  FormLabel,
  Divider,
  Badge,
  useToast
} from '@chakra-ui/react'
import { FiDownload, FiSave, FiFileText, FiEdit3 } from 'react-icons/fi'

interface Template {
  id: string
  name: string
  category: string
  variables: TemplateVariable[]
}

interface TemplateVariable {
  key: string
  label: string
  type: 'text' | 'number' | 'date' | 'select'
  required: boolean
  options?: string[]
}

export const DocumentGenerator = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [isGenerating, setIsGenerating] = useState(false)
  const toast = useToast()

  const templates: Template[] = [
    {
      id: '1',
      name: 'Contrato de Compraventa',
      category: 'Ventas',
      variables: [
        { key: 'buyer_name', label: 'Nombre del Comprador', type: 'text', required: true },
        { key: 'seller_name', label: 'Nombre del Vendedor', type: 'text', required: true },
        { key: 'property_address', label: 'Dirección de la Propiedad', type: 'text', required: true },
        { key: 'sale_price', label: 'Precio de Venta', type: 'number', required: true },
        { key: 'contract_date', label: 'Fecha del Contrato', type: 'date', required: true }
      ]
    },
    {
      id: '2',
      name: 'Contrato de Arrendamiento',
      category: 'Arriendos',
      variables: [
        { key: 'tenant_name', label: 'Nombre del Arrendatario', type: 'text', required: true },
        { key: 'landlord_name', label: 'Nombre del Arrendador', type: 'text', required: true },
        { key: 'property_address', label: 'Dirección de la Propiedad', type: 'text', required: true },
        { key: 'monthly_rent', label: 'Arriendo Mensual', type: 'number', required: true },
        { key: 'contract_duration', label: 'Duración del Contrato', type: 'select', required: true, options: ['6 meses', '1 año', '2 años'] }
      ]
    }
  ]

  const handleTemplateChange = (templateId: string) => {
    const template = templates.find(t => t.id === templateId)
    setSelectedTemplate(template || null)
    setFormData({})
  }

  const handleInputChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleGenerate = async () => {
    if (!selectedTemplate) return

    setIsGenerating(true)
    
    // Simular generación del documento
    setTimeout(() => {
      setIsGenerating(false)
      toast({
        title: 'Documento generado',
        description: 'El documento se ha generado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    }, 2000)
  }

  const isFormValid = () => {
    if (!selectedTemplate) return false
    
    return selectedTemplate.variables
      .filter(v => v.required)
      .every(v => formData[v.key] && formData[v.key].toString().trim() !== '')
  }

  const renderFormField = (variable: TemplateVariable) => {
    const commonProps = {
      value: formData[variable.key] || '',
      onChange: (e: any) => handleInputChange(variable.key, e.target.value),
      isRequired: variable.required
    }

    switch (variable.type) {
      case 'select':
        return (
          <Select placeholder={`Selecciona ${variable.label}`} {...commonProps}>
            {variable.options?.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </Select>
        )
      case 'number':
        return <Input type="number" placeholder={variable.label} {...commonProps} />
      case 'date':
        return <Input type="date" {...commonProps} />
      case 'text':
      default:
        return <Input placeholder={variable.label} {...commonProps} />
    }
  }

  return (
    <Box p={6} maxW="4xl" mx="auto">
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" color="text" mb={2}>
            Generador de Documentos
          </Heading>
          <Text color="text.muted">
            Genera documentos legales usando plantillas predefinidas
          </Text>
        </Box>

        <Divider borderColor="border" />

        {/* Template Selection */}
        <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
          <VStack spacing={4} align="stretch">
            <Heading size="md" color="text">
              1. Selecciona una Plantilla
            </Heading>
            
            <FormControl>
              <FormLabel color="text.muted">Tipo de Documento</FormLabel>
              <Select
                placeholder="Selecciona una plantilla..."
                onChange={(e) => handleTemplateChange(e.target.value)}
              >
                {templates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name} ({template.category})
                  </option>
                ))}
              </Select>
            </FormControl>

            {selectedTemplate && (
              <Box p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="semibold" color="blue.800">
                      {selectedTemplate.name}
                    </Text>
                    <Text fontSize="sm" color="blue.600">
                      Categoría: {selectedTemplate.category}
                    </Text>
                  </VStack>
                  <Badge colorScheme="blue">
                    {selectedTemplate.variables.length} campos
                  </Badge>
                </HStack>
              </Box>
            )}
          </VStack>
        </Box>

        {/* Form Fields */}
        {selectedTemplate && (
          <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
            <VStack spacing={4} align="stretch">
              <Heading size="md" color="text">
                2. Completa la Información
              </Heading>

              <VStack spacing={4}>
                {selectedTemplate.variables.map(variable => (
                  <FormControl key={variable.key} isRequired={variable.required}>
                    <FormLabel color="text.muted">
                      {variable.label}
                      {variable.required && <Text as="span" color="red.400"> *</Text>}
                    </FormLabel>
                    {renderFormField(variable)}
                  </FormControl>
                ))}
              </VStack>
            </VStack>
          </Box>
        )}

        {/* Actions */}
        {selectedTemplate && (
          <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
            <VStack spacing={4} align="stretch">
              <Heading size="md" color="text">
                3. Generar Documento
              </Heading>

              <HStack spacing={3}>
                <Button
                  colorScheme="blue"
                  leftIcon={<FiFileText />}
                  isLoading={isGenerating}
                  loadingText="Generando..."
                  isDisabled={!isFormValid()}
                  onClick={handleGenerate}
                >
                  Generar Documento
                </Button>

                <Button
                  variant="outline"
                  borderColor="border"
                  color="text"
                  leftIcon={<FiSave />}
                  isDisabled={!isFormValid()}
                >
                  Guardar Borrador
                </Button>

                <Button
                  variant="outline"
                  borderColor="border"
                  color="text"
                  leftIcon={<FiDownload />}
                  isDisabled={!isFormValid()}
                >
                  Descargar
                </Button>
              </HStack>

              {!isFormValid() && selectedTemplate && (
                <Text fontSize="sm" color="orange.400">
                  * Completa todos los campos requeridos para continuar
                </Text>
              )}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
