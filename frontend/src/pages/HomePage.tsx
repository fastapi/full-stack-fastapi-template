import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  Grid,
  Flex,
  VStack,
  HStack,
  Icon,
  Badge,
  Card,
  CardBody,
  Image,
  Divider,
  Stack,
  useColorModeValue,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  Avatar,
  AvatarGroup
} from '@chakra-ui/react';
import {
  FiHome,
  FiDollarSign,
  FiShield,
  FiTrendingUp,
  FiUsers,
  FiStar,
  FiAward,
  FiCheckCircle,
  FiArrowRight,
  FiPhone,
  FiMail,
  FiMapPin,
  FiClock
} from 'react-icons/fi';

const HomePage: React.FC = () => {
  const [stats] = useState({
    properties: 1247,
    loans: 856,
    clients: 2341,
    satisfaction: 98
  });

  // Hero Section
  const HeroSection = () => (
    <Box
      position="relative"
      minH="100vh"
      bg="linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(45,55,72,0.9) 50%, rgba(0,0,0,0.8) 100%)"
      overflow="hidden"
    >
      {/* Background Image - TU FONDO GENIUS */}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bgImage="url('/fondo_genius.png')"
        bgSize="cover"
        bgPosition="center"
        bgRepeat="no-repeat"
        opacity={0.3}
      />

      <Container maxW="7xl" position="relative" zIndex={1}>
        <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={12} alignItems="center" minH="100vh">
          {/* Left Column - Content */}
          <Box>
            <VStack align="start" gap={8}>
              {/* Logo */}
              <Flex align="center">
                <Box
                  w={20}
                  h={20}
                  bg="white"
                  color="black"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  mr={4}
                  fontWeight="bold"
                  fontSize="2xl"
                  borderRadius="xl"
                  shadow="2xl"
                >
                  GI
                </Box>
                <VStack align="start" gap={0}>
                  <Heading size="xl" color="white">
                    GENIUS
                  </Heading>
                  <Heading size="xl" color="white">
                    INDUSTRIES
                  </Heading>
                </VStack>
              </Flex>

              {/* Main Headline */}
              <VStack align="start" gap={4}>
                <Heading
                  as="h1"
                  size="3xl"
                  color="white"
                  lineHeight="1.2"
                  fontWeight="black"
                  textShadow="2px 2px 4px rgba(0,0,0,0.8)"
                >
                  Innovamos el Futuro
                  <Text as="span" color="gray.200" display="block">
                    Inmobiliario y Financiero
                  </Text>
                </Heading>
                
                <Text fontSize="xl" color="gray.200" maxW="lg" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
                  Soluciones integrales en bienes raíces y servicios financieros 
                  con tecnología de vanguardia y excelencia en el servicio.
                </Text>
              </VStack>

              {/* CTAs */}
              <HStack gap={4}>
                <Button
                  size="lg"
                  bg="white"
                  color="black"
                  _hover={{
                    bg: 'gray.100',
                    transform: 'translateY(-2px)',
                    shadow: '2xl'
                  }}
                  rightIcon={<Icon as={FiArrowRight} />}
                  px={8}
                  py={6}
                  borderRadius="xl"
                  fontWeight="bold"
                  transition="all 0.3s"
                >
                  Explorar Propiedades
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  borderColor="white"
                  color="white"
                  _hover={{
                    bg: 'white',
                    color: 'black',
                    transform: 'translateY(-2px)'
                  }}
                  px={8}
                  py={6}
                  borderRadius="xl"
                  fontWeight="bold"
                  transition="all 0.3s"
                >
                  Servicios Financieros
                </Button>
              </HStack>

              {/* Trust Indicators */}
              <HStack gap={8} pt={4}>
                <VStack gap={1}>
                  <Text color="white" fontSize="2xl" fontWeight="bold" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
                    {stats.properties.toLocaleString()}+
                  </Text>
                  <Text color="gray.300" fontSize="sm">
                    Propiedades
                  </Text>
                </VStack>
                <VStack gap={1}>
                  <Text color="white" fontSize="2xl" fontWeight="bold" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
                    {stats.clients.toLocaleString()}+
                  </Text>
                  <Text color="gray.300" fontSize="sm">
                    Clientes Satisfechos
                  </Text>
                </VStack>
                <VStack gap={1}>
                  <Text color="white" fontSize="2xl" fontWeight="bold" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
                    {stats.satisfaction}%
                  </Text>
                  <Text color="gray.300" fontSize="sm">
                    Satisfacción
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </Box>

          {/* Right Column - Visual */}
          <Box>
            <Box position="relative">
              {/* Main Image Placeholder */}
              <Box
                w="full"
                h="600px"
                bg="rgba(0,0,0,0.4)"
                borderRadius="2xl"
                overflow="hidden"
                position="relative"
                border="2px solid"
                borderColor="whiteAlpha.300"
                backdropFilter="blur(10px)"
              >
                {/* Your Background Image */}
                <Box
                  position="absolute"
                  top={0}
                  left={0}
                  right={0}
                  bottom={0}
                  bgImage="url('/fondo_genius.png')"
                  bgSize="cover"
                  bgPosition="center"
                  opacity={0.6}
                />
                
                {/* Gradient Overlay */}
                <Box
                  position="absolute"
                  top={0}
                  left={0}
                  right={0}
                  bottom={0}
                  bg="linear-gradient(45deg, rgba(0,0,0,0.4), rgba(255,255,255,0.1))"
                />
                
                {/* Building Silhouette */}
                <Flex
                  position="absolute"
                  bottom={0}
                  left={0}
                  right={0}
                  height="60%"
                  align="end"
                  justify="center"
                  px={8}
                >
                  {[120, 180, 150, 200, 160, 140].map((height, index) => (
                    <Box
                      key={index}
                      width="50px"
                      height={`${height}px`}
                      bg="rgba(255,255,255,0.1)"
                      mx={1}
                      borderRadius="sm"
                      backdropFilter="blur(5px)"
                    />
                  ))}
                </Flex>

                {/* Floating Cards */}
                <Box
                  position="absolute"
                  top="20%"
                  right="10%"
                >
                  <Card bg="white" shadow="2xl" borderRadius="xl" p={4}>
                    <CardBody>
                      <HStack>
                        <Icon as={FiTrendingUp} color="green.500" w={6} h={6} />
                        <VStack align="start" gap={0}>
                          <Text fontSize="sm" color="gray.600">ROI Promedio</Text>
                          <Text fontSize="lg" fontWeight="bold" color="black">+15.2%</Text>
                        </VStack>
                      </HStack>
                    </CardBody>
                  </Card>
                </Box>

                <Box
                  position="absolute"
                  bottom="25%"
                  left="5%"
                >
                  <Card bg="white" shadow="2xl" borderRadius="xl" p={4}>
                    <CardBody>
                      <HStack>
                        <Icon as={FiShield} color="blue.500" w={6} h={6} />
                        <VStack align="start" gap={0}>
                          <Text fontSize="sm" color="gray.600">Seguridad</Text>
                          <Text fontSize="lg" fontWeight="bold" color="black">100% Garantizada</Text>
                        </VStack>
                      </HStack>
                    </CardBody>
                  </Card>
                </Box>
              </Box>
            </Box>
          </Box>
        </Grid>
      </Container>
    </Box>
  );

  // Services Section
  const ServicesSection = () => (
    <Box bg="white" py={20}>
      <Container maxW="7xl">
        <VStack gap={16}>
          {/* Section Header */}
          <VStack gap={4} textAlign="center">
            <Badge colorScheme="gray" fontSize="sm" px={4} py={2} borderRadius="full">
              NUESTROS SERVICIOS
            </Badge>
            <Heading size="2xl" color="black">
              Soluciones Integrales para tu Futuro
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="2xl">
              Combinamos experiencia inmobiliaria con servicios financieros 
              innovadores para maximizar tu inversión y patrimonio.
            </Text>
          </VStack>

          {/* Services Grid */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={8} w="full">
            {[
              {
                icon: FiHome,
                title: 'Bienes Raíces',
                description: 'Compra, venta y alquiler de propiedades residenciales y comerciales con asesoría experta.',
                features: ['Valoraciones profesionales', 'Gestión integral', 'Marketing digital'],
                color: 'blue'
              },
              {
                icon: FiDollarSign,
                title: 'Servicios Financieros',
                description: 'Préstamos hipotecarios, personales y soluciones de inversión adaptadas a tus necesidades.',
                features: ['Tasas competitivas', 'Aprobación rápida', 'Asesoría personalizada'],
                color: 'green'
              },
              {
                icon: FiShield,
                title: 'Gestión Legal',
                description: 'Documentación legal completa y cumplimiento normativo para todas tus transacciones.',
                features: ['Contratos seguros', 'Compliance total', 'Auditorías regulares'],
                color: 'purple'
              }
            ].map((service, index) => (
              <Card
                key={index}
                _hover={{
                  transform: 'translateY(-8px)',
                  shadow: '2xl'
                }}
                transition="all 0.3s"
                borderRadius="2xl"
                overflow="hidden"
                border="1px solid"
                borderColor="gray.100"
              >
                <CardBody p={8}>
                  <VStack align="start" gap={6}>
                    <Box
                      p={4}
                      bg={`${service.color}.50`}
                      borderRadius="xl"
                      display="inline-block"
                    >
                      <Icon as={service.icon} w={8} h={8} color={`${service.color}.500`} />
                    </Box>
                    
                    <VStack align="start" gap={3}>
                      <Heading size="lg" color="black">
                        {service.title}
                      </Heading>
                      <Text color="gray.600" lineHeight="tall">
                        {service.description}
                      </Text>
                    </VStack>

                    <VStack align="start" gap={2} w="full">
                      {service.features.map((feature, idx) => (
                        <HStack key={idx}>
                          <Icon as={FiCheckCircle} w={4} h={4} color={`${service.color}.500`} />
                          <Text fontSize="sm" color="gray.700">{feature}</Text>
                        </HStack>
                      ))}
                    </VStack>

                    <Button
                      variant="ghost"
                      color={`${service.color}.500`}
                      rightIcon={<Icon as={FiArrowRight} />}
                      _hover={{ bg: `${service.color}.50` }}
                      p={0}
                    >
                      Conocer más
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );

  // Stats Section
  const StatsSection = () => (
    <Box 
      bg="black" 
      py={20} 
      position="relative" 
      overflow="hidden"
      backgroundImage="url('/fondo_genius.png')"
      backgroundSize="cover"
      backgroundPosition="center"
      backgroundAttachment="fixed"
    >
      {/* Dark Overlay */}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bg="rgba(0,0,0,0.8)"
      />

      <Container maxW="7xl" position="relative" zIndex={1}>
        <VStack gap={16}>
          <VStack gap={4} textAlign="center">
            <Heading size="2xl" color="white" textShadow="2px 2px 4px rgba(0,0,0,0.8)">
              Números que Hablan por Nosotros
            </Heading>
            <Text fontSize="xl" color="gray.200" maxW="2xl" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
              Más de una década construyendo confianza y generando resultados excepcionales.
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 2, md: 4 }} gap={8} w="full">
            {[
              { number: '1,247', label: 'Propiedades Gestionadas', icon: FiHome },
              { number: '2,341', label: 'Clientes Satisfechos', icon: FiUsers },
              { number: '$125M', label: 'Volumen Transaccional', icon: FiDollarSign },
              { number: '98%', label: 'Tasa de Satisfacción', icon: FiStar }
            ].map((stat, index) => (
              <Box
                key={index}
                textAlign="center"
              >
                <VStack gap={4}>
                  <Box
                    p={4}
                    bg="white"
                    borderRadius="full"
                    display="inline-block"
                  >
                    <Icon as={stat.icon} w={8} h={8} color="black" />
                  </Box>
                  <VStack gap={1}>
                    <Text fontSize="4xl" fontWeight="black" color="white" textShadow="2px 2px 4px rgba(0,0,0,0.8)">
                      {stat.number}
                    </Text>
                    <Text color="gray.200" fontSize="lg" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
                      {stat.label}
                    </Text>
                  </VStack>
                </VStack>
              </Box>
            ))}
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );

  // Testimonials Section
  const TestimonialsSection = () => (
    <Box bg="gray.50" py={20}>
      <Container maxW="7xl">
        <VStack gap={16}>
          <VStack gap={4} textAlign="center">
            <Badge colorScheme="gray" fontSize="sm" px={4} py={2} borderRadius="full">
              TESTIMONIOS
            </Badge>
            <Heading size="2xl" color="black">
              Lo que Dicen Nuestros Clientes
            </Heading>
          </VStack>

          <SimpleGrid columns={{ base: 1, lg: 3 }} gap={8}>
            {[
              {
                name: 'María González',
                role: 'Inversora Inmobiliaria',
                avatar: 'MG',
                text: 'GENIUS INDUSTRIES transformó mi visión de inversión. Su plataforma integral me permitió diversificar mi portfolio de manera inteligente.',
                rating: 5
              },
              {
                name: 'Carlos Rodríguez',
                role: 'Empresario',
                avatar: 'CR',
                text: 'El servicio financiero excepcional y la atención personalizada han sido clave para el crecimiento de mis negocios.',
                rating: 5
              },
              {
                name: 'Ana Martínez',
                role: 'Compradora de Vivienda',
                avatar: 'AM',
                text: 'Proceso de compra sin complicaciones. El equipo me guió en cada paso hasta encontrar la casa de mis sueños.',
                rating: 5
              }
            ].map((testimonial, index) => (
              <Card
                key={index}
                bg="white"
                borderRadius="2xl"
                shadow="lg"
                border="1px solid"
                borderColor="gray.100"
                _hover={{
                  transform: 'translateY(-4px)',
                  shadow: 'xl'
                }}
                transition="all 0.3s"
              >
                <CardBody p={8}>
                  <VStack gap={6}>
                    <HStack gap={1}>
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Icon key={i} as={FiStar} color="yellow.400" w={5} h={5} />
                      ))}
                    </HStack>
                    
                    <Text
                      color="gray.700"
                      fontSize="lg"
                      lineHeight="tall"
                      textAlign="center"
                      fontStyle="italic"
                    >
                      "{testimonial.text}"
                    </Text>
                    
                    <VStack gap={2}>
                      <Avatar bg="black" color="white" name={testimonial.name}>
                        {testimonial.avatar}
                      </Avatar>
                      <VStack gap={0}>
                        <Text fontWeight="bold" color="black">
                          {testimonial.name}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          {testimonial.role}
                        </Text>
                      </VStack>
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

  // CTA Section
  const CTASection = () => (
    <Box bg="white" py={20}>
      <Container maxW="5xl">
        <Card
          bg="linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(45,55,72,0.9) 100%)"
          borderRadius="3xl"
          overflow="hidden"
          position="relative"
          backgroundImage="url('/fondo_genius.png')"
          backgroundSize="cover"
          backgroundPosition="center"
        >
          {/* Dark Overlay */}
          <Box
            position="absolute"
            top={0}
            left={0}
            right={0}
            bottom={0}
            bg="rgba(0,0,0,0.7)"
          />
          
          <CardBody p={16} position="relative" zIndex={1}>
            <VStack gap={8} textAlign="center">
              <VStack gap={4}>
                <Heading size="2xl" color="white" textShadow="2px 2px 4px rgba(0,0,0,0.8)">
                  ¿Listo para Comenzar tu Próxima Inversión?
                </Heading>
                <Text fontSize="xl" color="gray.200" maxW="2xl" textShadow="1px 1px 2px rgba(0,0,0,0.8)">
                  Únete a miles de clientes que ya confían en GENIUS INDUSTRIES 
                  para hacer crecer su patrimonio.
                </Text>
              </VStack>
              
              <HStack gap={4}>
                <Button
                  size="lg"
                  bg="white"
                  color="black"
                  _hover={{
                    bg: 'gray.100',
                    transform: 'translateY(-2px)'
                  }}
                  px={8}
                  py={6}
                  borderRadius="xl"
                  fontWeight="bold"
                >
                  Agenda una Consulta
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  borderColor="white"
                  color="white"
                  _hover={{
                    bg: 'white',
                    color: 'black'
                  }}
                  px={8}
                  py={6}
                  borderRadius="xl"
                  fontWeight="bold"
                >
                  Ver Catálogo
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      </Container>
    </Box>
  );

  return (
    <Box>
      <HeroSection />
      <ServicesSection />
      <StatsSection />
      <TestimonialsSection />
      <CTASection />
    </Box>
  );
};

export default HomePage; 