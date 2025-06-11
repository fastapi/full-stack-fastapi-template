import React from 'react';
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
  Badge,
  Card,
  CardBody,
  Image,
  Divider,
  SimpleGrid,
  Avatar,
  Progress,
  Timeline,
  TimelineItem,
  TimelineConnector,
  TimelineContent,
  TimelineDescription,
  TimelineRoot,
  TimelineTitle
} from '@chakra-ui/react';
import {
  FiUsers,
  FiTrendingUp,
  FiShield,
  FiAward,
  FiGlobe,
  FiHeart,
  FiTarget,
  FiEye,
  FiStar,
  FiCheckCircle,
  FiBuilding,
  FiDollarSign
} from 'react-icons/fi';

const AboutPage: React.FC = () => {
  // Hero Section
  const HeroSection = () => (
    <Box
      position="relative"
      py={20}
      bg="linear-gradient(135deg, #000000 0%, #2D3748 100%)"
      overflow="hidden"
    >
      <Container maxW="7xl" position="relative" zIndex={1}>
        <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={12} alignItems="center">
          {/* Left Column */}
          <VStack align="start" spacing={8}>
            <VStack align="start" spacing={4}>
              <Badge colorScheme="whiteAlpha" fontSize="sm" px={4} py={2} borderRadius="full">
                CONÓCENOS
              </Badge>
              <Heading
                size="3xl"
                color="white"
                lineHeight="1.2"
                fontWeight="black"
              >
                Transformando el
                <Text as="span" color="gray.300" display="block">
                  Sector Inmobiliario
                </Text>
              </Heading>
              <Text fontSize="xl" color="gray.300" maxW="lg">
                Con más de una década de experiencia, GENIUS INDUSTRIES ha revolucionado 
                la forma en que las personas invierten en bienes raíces y acceden a 
                servicios financieros.
              </Text>
            </VStack>
            
            <Grid templateColumns="repeat(3, 1fr)" gap={8} w="full">
              <VStack spacing={2}>
                <Text color="white" fontSize="3xl" fontWeight="bold">15+</Text>
                <Text color="gray.400" fontSize="sm" textAlign="center">Años de Experiencia</Text>
              </VStack>
              <VStack spacing={2}>
                <Text color="white" fontSize="3xl" fontWeight="bold">50+</Text>
                <Text color="gray.400" fontSize="sm" textAlign="center">Profesionales</Text>
              </VStack>
              <VStack spacing={2}>
                <Text color="white" fontSize="3xl" fontWeight="bold">10+</Text>
                <Text color="gray.400" fontSize="sm" textAlign="center">Ciudades</Text>
              </VStack>
            </Grid>
          </VStack>

          {/* Right Column */}
          <Box position="relative">
            <Box
              w="full"
              h="500px"
              bg="gray.800"
              borderRadius="2xl"
              overflow="hidden"
              border="1px solid"
              borderColor="gray.600"
              position="relative"
            >
              {/* Placeholder for company photo */}
              <Flex align="center" justify="center" h="full" direction="column">
                <Icon as={FiBuilding} w={24} h={24} color="gray.500" mb={4} />
                <Text color="gray.500" fontSize="lg">Oficinas GENIUS INDUSTRIES</Text>
              </Flex>
            </Box>
          </Box>
        </Grid>
      </Container>
    </Box>
  );

  // Mission & Vision Section
  const MissionVisionSection = () => (
    <Box bg="white" py={20}>
      <Container maxW="7xl">
        <VStack spacing={16}>
          {/* Section Header */}
          <VStack spacing={4} textAlign="center">
            <Heading size="2xl" color="black">
              Nuestra Esencia
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="3xl">
              Los valores y principios que guían cada decisión en GENIUS INDUSTRIES
            </Text>
          </VStack>

          {/* Mission, Vision, Values Grid */}
          <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={8} w="full">
            {/* Mission */}
            <Card
              borderRadius="2xl"
              overflow="hidden"
              border="1px solid"
              borderColor="gray.100"
              bg="blue.50"
            >
              <CardBody p={8}>
                <VStack spacing={6} align="start">
                  <Box
                    p={4}
                    bg="blue.500"
                    borderRadius="xl"
                    display="inline-block"
                  >
                    <Icon as={FiTarget} w={8} h={8} color="white" />
                  </Box>
                  
                  <VStack align="start" spacing={3}>
                    <Heading size="lg" color="black">
                      Nuestra Misión
                    </Heading>
                    <Text color="gray.700" lineHeight="tall">
                      Democratizar el acceso a servicios inmobiliarios y financieros 
                      de calidad, utilizando tecnología innovadora para crear valor 
                      sostenible para nuestros clientes y comunidades.
                    </Text>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Vision */}
            <Card
              borderRadius="2xl"
              overflow="hidden"
              border="1px solid"
              borderColor="gray.100"
              bg="purple.50"
            >
              <CardBody p={8}>
                <VStack spacing={6} align="start">
                  <Box
                    p={4}
                    bg="purple.500"
                    borderRadius="xl"
                    display="inline-block"
                  >
                    <Icon as={FiEye} w={8} h={8} color="white" />
                  </Box>
                  
                  <VStack align="start" spacing={3}>
                    <Heading size="lg" color="black">
                      Nuestra Visión
                    </Heading>
                    <Text color="gray.700" lineHeight="tall">
                      Ser la plataforma líder en América Latina que conecte personas 
                      con oportunidades inmobiliarias y financieras, transformando 
                      la forma en que construyen su patrimonio.
                    </Text>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Values */}
            <Card
              borderRadius="2xl"
              overflow="hidden"
              border="1px solid"
              borderColor="gray.100"
              bg="green.50"
            >
              <CardBody p={8}>
                <VStack spacing={6} align="start">
                  <Box
                    p={4}
                    bg="green.500"
                    borderRadius="xl"
                    display="inline-block"
                  >
                    <Icon as={FiHeart} w={8} h={8} color="white" />
                  </Box>
                  
                  <VStack align="start" spacing={3}>
                    <Heading size="lg" color="black">
                      Nuestros Valores
                    </Heading>
                    <VStack align="start" spacing={2}>
                      {[
                        'Transparencia total',
                        'Innovación constante',
                        'Excelencia en el servicio',
                        'Compromiso social',
                        'Integridad absoluta'
                      ].map((value, index) => (
                        <HStack key={index}>
                          <Icon as={FiCheckCircle} w={4} h={4} color="green.500" />
                          <Text fontSize="sm" color="gray.700">{value}</Text>
                        </HStack>
                      ))}
                    </VStack>
                  </VStack>
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );

  // Timeline Section
  const TimelineSection = () => (
    <Box bg="gray.50" py={20}>
      <Container maxW="5xl">
        <VStack spacing={12}>
          <VStack spacing={4} textAlign="center">
            <Badge colorScheme="gray" fontSize="sm" px={4} py={2} borderRadius="full">
              NUESTRA HISTORIA
            </Badge>
            <Heading size="2xl" color="black">
              Construyendo el Futuro Paso a Paso
            </Heading>
          </VStack>

          <Box w="full">
            <TimelineRoot>
              {[
                {
                  year: '2010',
                  title: 'Fundación de GENIUS INDUSTRIES',
                  description: 'Iniciamos como una pequeña consultora inmobiliaria con la visión de transformar el sector.',
                  color: 'blue'
                },
                {
                  year: '2014',
                  title: 'Expansión a Servicios Financieros',
                  description: 'Agregamos préstamos hipotecarios y servicios financieros para completar nuestro ecosistema.',
                  color: 'green'
                },
                {
                  year: '2018',
                  title: 'Transformación Digital',
                  description: 'Lanzamos nuestra plataforma digital y sistema de gestión legal automatizado.',
                  color: 'purple'
                },
                {
                  year: '2021',
                  title: 'Certificación Internacional',
                  description: 'Obtuvimos certificaciones internacionales en compliance y gestión de riesgos.',
                  color: 'orange'
                },
                {
                  year: '2024',
                  title: 'Líder en Innovación',
                  description: 'Reconocidos como la empresa más innovadora del sector inmobiliario en la región.',
                  color: 'red'
                }
              ].map((milestone, index) => (
                <TimelineItem key={index}>
                  <TimelineConnector>
                    <Box
                      w={4}
                      h={4}
                      bg={`${milestone.color}.500`}
                      borderRadius="full"
                    />
                  </TimelineConnector>
                  <TimelineContent>
                    <Card bg="white" shadow="md" borderRadius="xl">
                      <CardBody p={6}>
                        <VStack align="start" spacing={3}>
                          <HStack>
                            <Badge colorScheme={milestone.color} variant="solid">
                              {milestone.year}
                            </Badge>
                          </HStack>
                          <TimelineTitle fontSize="lg" fontWeight="bold" color="black">
                            {milestone.title}
                          </TimelineTitle>
                          <TimelineDescription color="gray.600">
                            {milestone.description}
                          </TimelineDescription>
                        </VStack>
                      </CardBody>
                    </Card>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </TimelineRoot>
          </Box>
        </VStack>
      </Container>
    </Box>
  );

  // Team Section
  const TeamSection = () => (
    <Box bg="white" py={20}>
      <Container maxW="7xl">
        <VStack spacing={16}>
          <VStack spacing={4} textAlign="center">
            <Badge colorScheme="gray" fontSize="sm" px={4} py={2} borderRadius="full">
              NUESTRO EQUIPO
            </Badge>
            <Heading size="2xl" color="black">
              Los Expertos Detrás de GENIUS INDUSTRIES
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="3xl">
              Un equipo multidisciplinario de profesionales apasionados por la innovación 
              y comprometidos con la excelencia.
            </Text>
          </VStack>

          {/* Leadership Team */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8} w="full">
            {[
              {
                name: 'Carlos Mendoza',
                role: 'CEO & Fundador',
                avatar: 'CM',
                experience: '20+ años en bienes raíces',
                specialty: 'Estrategia corporativa'
              },
              {
                name: 'Ana Rodriguez',
                role: 'CTO',
                avatar: 'AR',
                experience: '15+ años en tecnología',
                specialty: 'Transformación digital'
              },
              {
                name: 'Miguel Santos',
                role: 'CFO',
                avatar: 'MS',
                experience: '18+ años en finanzas',
                specialty: 'Gestión financiera'
              },
              {
                name: 'Laura Jiménez',
                role: 'Directora Legal',
                avatar: 'LJ',
                experience: '12+ años en derecho',
                specialty: 'Compliance y regulación'
              }
            ].map((member, index) => (
              <Card
                key={index}
                borderRadius="2xl"
                overflow="hidden"
                border="1px solid"
                borderColor="gray.100"
                _hover={{
                  transform: 'translateY(-4px)',
                  shadow: 'xl'
                }}
                transition="all 0.3s"
              >
                <CardBody p={6} textAlign="center">
                  <VStack spacing={4}>
                    <Avatar
                      size="xl"
                      bg="black"
                      color="white"
                      name={member.name}
                    >
                      {member.avatar}
                    </Avatar>
                    
                    <VStack spacing={1}>
                      <Heading size="md" color="black">
                        {member.name}
                      </Heading>
                      <Text color="gray.600" fontWeight="semibold">
                        {member.role}
                      </Text>
                      <Text fontSize="sm" color="gray.500">
                        {member.experience}
                      </Text>
                      <Badge colorScheme="gray" variant="subtle" fontSize="xs">
                        {member.specialty}
                      </Badge>
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

  // Awards Section
  const AwardsSection = () => (
    <Box bg="black" py={20}>
      <Container maxW="7xl">
        <VStack spacing={16}>
          <VStack spacing={4} textAlign="center">
            <Heading size="2xl" color="white">
              Reconocimientos y Certificaciones
            </Heading>
            <Text fontSize="xl" color="gray.300" maxW="3xl">
              La excelencia reconocida por las principales instituciones del sector
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8} w="full">
            {[
              {
                title: 'Mejor Empresa Inmobiliaria',
                year: '2024',
                entity: 'Cámara de Comercio',
                icon: FiAward
              },
              {
                title: 'Innovación Tecnológica',
                year: '2023',
                entity: 'Tech Awards',
                icon: FiTrendingUp
              },
              {
                title: 'Excelencia en Servicio',
                year: '2023',
                entity: 'Customer Choice',
                icon: FiStar
              },
              {
                title: 'Responsabilidad Social',
                year: '2022',
                entity: 'Green Business',
                icon: FiGlobe
              }
            ].map((award, index) => (
              <Card
                key={index}
                bg="gray.800"
                borderRadius="xl"
                border="1px solid"
                borderColor="gray.600"
              >
                <CardBody p={6} textAlign="center">
                  <VStack spacing={4}>
                    <Box
                      p={3}
                      bg="white"
                      borderRadius="full"
                      display="inline-block"
                    >
                      <Icon as={award.icon} w={6} h={6} color="black" />
                    </Box>
                    
                    <VStack spacing={1}>
                      <Badge colorScheme="yellow" variant="solid">
                        {award.year}
                      </Badge>
                      <Heading size="sm" color="white" textAlign="center">
                        {award.title}
                      </Heading>
                      <Text fontSize="sm" color="gray.400">
                        {award.entity}
                      </Text>
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

  // Stats Section
  const StatsSection = () => (
    <Box bg="gray.50" py={20}>
      <Container maxW="7xl">
        <VStack spacing={16}>
          <VStack spacing={4} textAlign="center">
            <Heading size="2xl" color="black">
              Impacto en Números
            </Heading>
          </VStack>

          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={8} w="full">
            {[
              { number: '$125M+', label: 'Transacciones Gestionadas', progress: 100 },
              { number: '2,341', label: 'Familias Beneficiadas', progress: 85 },
              { number: '156', label: 'Proyectos Completados', progress: 90 },
              { number: '98%', label: 'Satisfacción del Cliente', progress: 98 }
            ].map((stat, index) => (
              <Card
                key={index}
                bg="white"
                borderRadius="xl"
                border="1px solid"
                borderColor="gray.200"
                p={6}
              >
                <VStack spacing={4}>
                  <VStack spacing={1}>
                    <Text fontSize="3xl" fontWeight="black" color="black">
                      {stat.number}
                    </Text>
                    <Text color="gray.600" fontSize="sm" textAlign="center">
                      {stat.label}
                    </Text>
                  </VStack>
                  <Progress
                    value={stat.progress}
                    colorScheme="black"
                    size="sm"
                    w="full"
                    borderRadius="full"
                  />
                </VStack>
              </Card>
            ))}
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );

  return (
    <Box>
      <HeroSection />
      <MissionVisionSection />
      <TimelineSection />
      <TeamSection />
      <AwardsSection />
      <StatsSection />
    </Box>
  );
};

export default AboutPage; 