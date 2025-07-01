import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Grid,
  Card,
  CardBody,
  CardHeader,
  Button,
  Icon,
  Flex,
  Badge,
  HStack,
  VStack,
  Input
} from '@chakra-ui/react';
import { FiFileText, FiArrowLeft, FiArrowRight, FiEye, FiSave, FiDownload } from 'react-icons/fi';

const DocumentGenerator: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);

  const steps = [
    { title: 'Seleccionar Template', description: 'Elige el tipo de documento' },
    { title: 'Completar Datos', description: 'Llena la información requerida' },
    { title: 'Vista Previa', description: 'Revisa el documento generado' },
    { title: 'Finalizar', description: 'Guarda y descarga el documento' }
  ];

  return (
    <Box maxW="7xl" mx="auto" px={6} py={8}>
      <Box mb={8}>
        <Flex align="center" mb={4}>
          <Box 
            w={12} 
            h={12} 
            bg="black" 
            color="white" 
            display="flex" 
            alignItems="center" 
            justifyContent="center" 
            mr={4}
            fontWeight="bold"
            fontSize="sm"
          >
            GI
          </Box>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="black">
              Generador de Documentos
            </Heading>
            <Text color="gray.600" fontSize="sm">
              GENIUS INDUSTRIES - Crea documentos legales profesionales
            </Text>
          </VStack>
        </Flex>
        <Box height="1px" bg="black" width="100%" />
      </Box>

      <Box mb={8}>
        <HStack spacing={4} mb={6} justify="center">
          {steps.map((step, index) => (
            <VStack key={index} spacing={2}>
              <Box 
                w={8} 
                h={8} 
                borderRadius="full" 
                bg={activeStep >= index ? "black" : "gray.200"} 
                color={activeStep >= index ? "white" : "gray.600"}
                display="flex" 
                alignItems="center" 
                justifyContent="center"
                fontWeight="bold"
                fontSize="sm"
              >
                {activeStep > index ? "✓" : (index + 1)}
              </Box>
              <Box textAlign="center">
                <Text fontWeight="semibold" fontSize="sm">{step.title}</Text>
                <Text fontSize="xs" color="gray.600">{step.description}</Text>
              </Box>
            </VStack>
          ))}
        </HStack>
      </Box>

      <Box mb={8}>
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <Heading size="lg" color="black" mb={2}>
              Generador de Documentos Legales
            </Heading>
            <Text color="gray.600">
              Herramienta para crear documentos profesionales
            </Text>
          </Box>
          
          <Card>
            <CardBody p={6}>
              <Text color="gray.600" textAlign="center">
                Componente en desarrollo...
              </Text>
            </CardBody>
          </Card>
        </VStack>
      </Box>

      <Flex justify="space-between" align="center">
        <Button 
          leftIcon={<Icon as={FiArrowLeft} />}
          variant="outline"
          borderColor="black"
          color="black"
          _hover={{ bg: 'black', color: 'white' }}
          onClick={() => setActiveStep(prev => Math.max(0, prev - 1))}
          isDisabled={activeStep === 0}
        >
          Anterior
        </Button>

        <Button 
          rightIcon={<Icon as={FiArrowRight} />}
          bg="black"
          color="white"
          _hover={{ bg: 'gray.800' }}
          onClick={() => setActiveStep(prev => Math.min(steps.length - 1, prev + 1))}
          isDisabled={activeStep === steps.length - 1}
        >
          Siguiente
        </Button>
      </Flex>
    </Box>
  );
};

export default DocumentGenerator;
