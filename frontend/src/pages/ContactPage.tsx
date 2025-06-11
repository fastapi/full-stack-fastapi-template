import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Grid,
  Flex,
  VStack,
  HStack,
  Icon,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  Button,
  Badge,
  Divider,
  SimpleGrid,
  useToast
} from '@chakra-ui/react';
import {
  FiPhone,
  FiMail,
  FiMapPin,
  FiClock,
  FiSend,
  FiUser,
  FiMessageSquare,
  FiBuilding,
  FiGlobe
} from 'react-icons/fi';

const ContactPage: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    service: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {
      toast({
        title: "Mensaje enviado exitosamente",
        description: "Nos contactaremos contigo en las próximas 24 horas.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      setIsSubmitting(false);
      setFormData({
        name: '',
        email: '',
        phone: '',
        subject: '',
        service: '',
        message: ''
      });
    }, 2000);
  };

  // Hero Section
  const HeroSection = () => (
    <Box
      position="relative"
      py={20}
      bg="linear-gradient(135deg, #000000 0%, #2D3748 100%)"
      overflow="hidden"
    >
      <Container maxW="7xl" position="relative" zIndex={1}>
        <VStack spacing={8} textAlign="center">
          <VStack spacing={4}>
            <Badge colorScheme="whiteAlpha" fontSize="sm" px={4} py={2} borderRadius="full">
              CONTACTO
            </Badge>
            <Heading
              size="3xl"
              color="white"
              lineHeight="1.2"
              fontWeight="black"
            >
              Conectemos y Construyamos
              <Text as="span" color="gray.300" display="block">
                tu Futuro Juntos
              </Text>
            </Heading>
            <Text fontSize="xl" color="gray.300" maxW="2xl">
              Estamos aquí para responder tus preguntas y ayudarte a encontrar 
              la solución perfecta para tus necesidades inmobiliarias y financieras.
            </Text>
          </VStack>

          <HStack spacing={8}>
            <VStack spacing={1}>
              <Text color="white" fontSize="2xl" fontWeight="bold">24/7</Text>
              <Text color="gray.400" fontSize="sm">Atención</Text>
            </VStack>
            <VStack spacing={1}>
              <Text color="white" fontSize="2xl" fontWeight="bold">&lt;2h</Text>
              <Text color="gray.400" fontSize="sm">Respuesta</Text>
            </VStack>
            <VStack spacing={1}>
              <Text color="white" fontSize="2xl" fontWeight="bold">100%</Text>
              <Text color="gray.400" fontSize="sm">Satisfacción</Text>
            </VStack>
          </HStack>
        </VStack>
      </Container>
    </Box>
  );

  // Contact Form & Info Section
  const ContactFormSection = () => (
    <Box bg="white" py={20}>
      <Container maxW="7xl">
        <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={12}>
          {/* Contact Form */}
          <Card borderRadius="2xl" shadow="xl" border="1px solid" borderColor="gray.100">
            <CardBody p={8}>
              <VStack spacing={6} align="start">
                <VStack spacing={2} align="start">
                  <Heading size="lg" color="black">
                    Envíanos un Mensaje
                  </Heading>
                  <Text color="gray.600">
                    Completa el formulario y nos contactaremos contigo lo antes posible.
                  </Text>
                </VStack>

                <Box as="form" onSubmit={handleSubmit} w="full">
                  <VStack spacing={4}>
                    <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4} w="full">
                      <FormControl isRequired>
                        <FormLabel color="black">Nombre Completo</FormLabel>
                        <Input
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          placeholder="Tu nombre completo"
                          focusBorderColor="black"
                        />
                      </FormControl>
                      
                      <FormControl isRequired>
                        <FormLabel color="black">Email</FormLabel>
                        <Input
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="tu.email@ejemplo.com"
                          focusBorderColor="black"
                        />
                      </FormControl>
                    </Grid>

                    <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4} w="full">
                      <FormControl>
                        <FormLabel color="black">Teléfono</FormLabel>
                        <Input
                          name="phone"
                          value={formData.phone}
                          onChange={handleInputChange}
                          placeholder="+57 (300) 123-4567"
                          focusBorderColor="black"
                        />
                      </FormControl>
                      
                      <FormControl isRequired>
                        <FormLabel color="black">Servicio de Interés</FormLabel>
                        <Select
                          name="service"
                          value={formData.service}
                          onChange={handleInputChange}
                          placeholder="Selecciona un servicio"
                          focusBorderColor="black"
                        >
                          <option value="bienes-raices">Bienes Raíces</option>
                          <option value="servicios-financieros">Servicios Financieros</option>
                          <option value="gestion-legal">Gestión Legal</option>
                          <option value="inversion">Asesoría de Inversión</option>
                          <option value="otro">Otro</option>
                        </Select>
                      </FormControl>
                    </Grid>

                    <FormControl isRequired>
                      <FormLabel color="black">Asunto</FormLabel>
                      <Input
                        name="subject"
                        value={formData.subject}
                        onChange={handleInputChange}
                        placeholder="¿En qué podemos ayudarte?"
                        focusBorderColor="black"
                      />
                    </FormControl>

                    <FormControl isRequired>
                      <FormLabel color="black">Mensaje</FormLabel>
                      <Textarea
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        placeholder="Comparte más detalles sobre tu consulta..."
                        rows={5}
                        focusBorderColor="black"
                      />
                    </FormControl>

                    <Button
                      type="submit"
                      bg="black"
                      color="white"
                      size="lg"
                      w="full"
                      _hover={{ bg: 'gray.800' }}
                      leftIcon={<Icon as={FiSend} />}
                      isLoading={isSubmitting}
                      loadingText="Enviando..."
                    >
                      Enviar Mensaje
                    </Button>
                  </VStack>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Contact Information */}
          <VStack spacing={6}>
            {/* Office Info */}
            <Card w="full" borderRadius="xl" border="1px solid" borderColor="gray.100">
              <CardBody p={6}>
                <VStack spacing={4} align="start">
                  <HStack>
                    <Box p={2} bg="black" borderRadius="lg">
                      <Icon as={FiMapPin} w={5} h={5} color="white" />
                    </Box>
                    <Heading size="md" color="black">Oficina Principal</Heading>
                  </HStack>
                  <VStack align="start" spacing={1}>
                    <Text color="gray.600">Carrera 15 #93-47, Piso 12</Text>
                    <Text color="gray.600">Bogotá, Colombia</Text>
                    <Text color="gray.600">Zona Rosa - Chapinero</Text>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Contact Methods */}
            <Card w="full" borderRadius="xl" border="1px solid" borderColor="gray.100">
              <CardBody p={6}>
                <VStack spacing={4} align="start">
                  <HStack>
                    <Box p={2} bg="black" borderRadius="lg">
                      <Icon as={FiPhone} w={5} h={5} color="white" />
                    </Box>
                    <Heading size="md" color="black">Contacto Directo</Heading>
                  </HStack>
                  <VStack align="start" spacing={2}>
                    <HStack>
                      <Icon as={FiPhone} w={4} h={4} color="gray.500" />
                      <Text color="gray.600">+57 (1) 123-4567</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiMail} w={4} h={4} color="gray.500" />
                      <Text color="gray.600">info@genius-industries.com</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiGlobe} w={4} h={4} color="gray.500" />
                      <Text color="gray.600">www.genius-industries.com</Text>
                    </HStack>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Business Hours */}
            <Card w="full" borderRadius="xl" border="1px solid" borderColor="gray.100">
              <CardBody p={6}>
                <VStack spacing={4} align="start">
                  <HStack>
                    <Box p={2} bg="black" borderRadius="lg">
                      <Icon as={FiClock} w={5} h={5} color="white" />
                    </Box>
                    <Heading size="md" color="black">Horarios de Atención</Heading>
                  </HStack>
                  <VStack align="start" spacing={1}>
                    <Text color="gray.600">Lunes - Viernes: 8:00 AM - 6:00 PM</Text>
                    <Text color="gray.600">Sábados: 9:00 AM - 2:00 PM</Text>
                    <Text color="gray.600">Domingos: Citas previa cita</Text>
                    <Badge colorScheme="green" variant="subtle" mt={2}>
                      Atención 24/7 para emergencias
                    </Badge>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </Grid>
      </Container>
    </Box>
  );

  // Offices Section
  const OfficesSection = () => (
    <Box bg="gray.50" py={20}>
      <Container maxW="7xl">
        <VStack spacing={12}>
          <VStack spacing={4} textAlign="center">
            <Badge colorScheme="gray" fontSize="sm" px={4} py={2} borderRadius="full">
              NUESTRAS OFICINAS
            </Badge>
            <Heading size="2xl" color="black">
              Presencia Nacional
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="3xl">
              Encuentra la oficina GENIUS INDUSTRIES más cercana a ti
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} w="full">
            {[
              {
                city: 'Bogotá',
                address: 'Carrera 15 #93-47, Piso 12',
                phone: '+57 (1) 123-4567',
                email: 'bogota@genius-industries.com',
                status: 'principal'
              },
              {
                city: 'Medellín',
                address: 'Calle 10 #40-50, El Poblado',
                phone: '+57 (4) 234-5678',
                email: 'medellin@genius-industries.com',
                status: 'sucursal'
              },
              {
                city: 'Cali',
                address: 'Av. 6 Norte #25-30, Granada',
                phone: '+57 (2) 345-6789',
                email: 'cali@genius-industries.com',
                status: 'sucursal'
              },
              {
                city: 'Barranquilla',
                address: 'Cra 53 #76-162, Norte',
                phone: '+57 (5) 456-7890',
                email: 'barranquilla@genius-industries.com',
                status: 'sucursal'
              },
              {
                city: 'Cartagena',
                address: 'Av. San Martín #8-89',
                phone: '+57 (5) 567-8901',
                email: 'cartagena@genius-industries.com',
                status: 'sucursal'
              },
              {
                city: 'Bucaramanga',
                address: 'Calle 36 #28-15, Cabecera',
                phone: '+57 (7) 678-9012',
                email: 'bucaramanga@genius-industries.com',
                status: 'sucursal'
              }
            ].map((office, index) => (
              <Card
                key={index}
                borderRadius="xl"
                border="1px solid"
                borderColor="gray.200"
                _hover={{
                  shadow: 'lg',
                  transform: 'translateY(-2px)'
                }}
                transition="all 0.3s"
              >
                <CardBody p={6}>
                  <VStack spacing={4} align="start">
                    <HStack justify="space-between" w="full">
                      <Heading size="md" color="black">
                        {office.city}
                      </Heading>
                      <Badge
                        colorScheme={office.status === 'principal' ? 'blue' : 'gray'}
                        variant="subtle"
                      >
                        {office.status === 'principal' ? 'Principal' : 'Sucursal'}
                      </Badge>
                    </HStack>
                    
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Icon as={FiMapPin} w={4} h={4} color="gray.500" />
                        <Text fontSize="sm" color="gray.600">{office.address}</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiPhone} w={4} h={4} color="gray.500" />
                        <Text fontSize="sm" color="gray.600">{office.phone}</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiMail} w={4} h={4} color="gray.500" />
                        <Text fontSize="sm" color="gray.600">{office.email}</Text>
                      </HStack>
                    </VStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );

  // FAQ Section
  const FAQSection = () => (
    <Box bg="white" py={20}>
      <Container maxW="5xl">
        <VStack spacing={12}>
          <VStack spacing={4} textAlign="center">
            <Heading size="2xl" color="black">
              Preguntas Frecuentes
            </Heading>
            <Text fontSize="xl" color="gray.600">
              Respuestas a las consultas más comunes
            </Text>
          </VStack>

          <VStack spacing={6} w="full">
            {[
              {
                question: '¿Qué servicios ofrece GENIUS INDUSTRIES?',
                answer: 'Ofrecemos servicios integrales de bienes raíces, servicios financieros y gestión legal. Desde compra y venta de propiedades hasta préstamos hipotecarios y documentación legal.'
              },
              {
                question: '¿Cuánto tiempo toma el proceso de aprobación de un préstamo?',
                answer: 'El proceso de aprobación típicamente toma entre 3-5 días hábiles. Nuestro equipo se encarga de agilizar todos los trámites para que obtengas una respuesta rápida.'
              },
              {
                question: '¿Ofrecen asesoría para inversionistas primerizos?',
                answer: 'Sí, contamos con un equipo especializado en asesoría para inversionistas nuevos. Te acompañamos desde la evaluación inicial hasta la gestión de tu portfolio.'
              },
              {
                question: '¿Qué documentos necesito para solicitar un préstamo?',
                answer: 'Los documentos básicos incluyen: cédula, certificado de ingresos, extractos bancarios de los últimos 3 meses, y avalúo del inmueble (si aplica).'
              }
            ].map((faq, index) => (
              <Card
                key={index}
                w="full"
                borderRadius="xl"
                border="1px solid"
                borderColor="gray.100"
              >
                <CardBody p={6}>
                  <VStack spacing={3} align="start">
                    <Heading size="sm" color="black">
                      {faq.question}
                    </Heading>
                    <Text color="gray.600" lineHeight="tall">
                      {faq.answer}
                    </Text>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </VStack>
        </VStack>
      </Container>
    </Box>
  );

  return (
    <Box>
      <HeroSection />
      <ContactFormSection />
      <OfficesSection />
      <FAQSection />
    </Box>
  );
};

export default ContactPage; 