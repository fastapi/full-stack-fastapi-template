import { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useToast,
  Textarea,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Avatar,
  Progress,
  useColorModeValue,
  Tooltip,
  Checkbox,
  CloseButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
} from '@chakra-ui/react';
import { 
  FiSave, 
  FiPlus, 
  FiTrash2, 
  FiEdit2, 
  FiEye, 
  FiEyeOff, 
  FiUpload, 
  FiDownload, 
  FiUser, 
  FiMail, 
  FiPhone, 
  FiLock, 
  FiGlobe,
  FiCreditCard,
  FiShield,
  FiBell,
  FiDatabase,
  FiUsers,
  FiHome,
  FiDollarSign,
  FiCheckCircle
} from 'react-icons/fi';

const Settings = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Datos de ejemplo
  const userProfile = {
    name: 'Admin User',
    email: 'admin@geniusindustries.com',
    phone: '+57 123 456 7890',
    role: 'Administrador',
    lastLogin: 'Hace 2 horas',
    avatar: 'https://bit.ly/dan-abramov',
  };

  const notificationSettings = {
    emailNotifications: true,
    pushNotifications: true,
    marketingEmails: false,
    securityAlerts: true,
    propertyUpdates: true,
  };

  const securitySettings = {
    twoFactorAuth: true,
    loginAlerts: true,
    deviceManagement: [
      { id: 1, name: 'MacBook Pro', os: 'macOS', lastUsed: 'Hace 2 horas', current: true },
      { id: 2, name: 'iPhone 13', os: 'iOS', lastUsed: 'Hace 3 días', current: false },
    ],
  };

  const handleSaveSettings = () => {
    toast({
      title: 'Configuración guardada',
      description: 'Tus cambios se han guardado correctamente.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const handleExportData = () => {
    toast({
      title: 'Datos exportados',
      description: 'Tus datos se han exportado correctamente.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const handleDeleteAccount = () => {
    // Lógica para eliminar la cuenta
    onClose();
    toast({
      title: 'Cuenta eliminada',
      description: 'Tu cuenta ha sido eliminada correctamente.',
      status: 'success',
      duration: 5000,
      isClosable: true,
    });
  };

  return (
    <Box p={6}>
      <VStack align="stretch" spacing={6}>
        {/* Encabezado */}
        <Box>
          <Heading size="lg">Configuración</Heading>
          <Text color="gray.500">Administra la configuración de tu cuenta y preferencias</Text>
        </Box>

        {/* Pestañas */}
        <Tabs variant="enclosed" onChange={(index) => setActiveTab(index)}>
          <TabList>
            <Tab>
              <HStack>
                <FiUser />
                <Text>Perfil</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack>
                <FiBell />
                <Text>Notificaciones</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack>
                <FiShield />
                <Text>Seguridad</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack>
                <FiDollarSign />
                <Text>Pagos</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack>
                <FiDatabase />
                <Text>Datos</Text>
              </HStack>
            </Tab>
          </TabList>

          <TabPanels mt={6}>
            {/* Pestaña de Perfil */}
            <TabPanel p={0}>
              <VStack spacing={6} align="stretch">
                <Card>
                  <CardHeader>
                    <Heading size="md">Información del Perfil</Heading>
                  </CardHeader>
                  <CardBody>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      <VStack spacing={6} align="stretch">
                        <FormControl>
                          <FormLabel>Nombre completo</FormLabel>
                          <Input value={userProfile.name} />
                        </FormControl>
                        <FormControl>
                          <FormLabel>Correo electrónico</FormLabel>
                          <Input type="email" value={userProfile.email} />
                        </FormControl>
                        <FormControl>
                          <FormLabel>Teléfono</FormLabel>
                          <Input type="tel" value={userProfile.phone} />
                        </FormControl>
                      </VStack>
                      <VStack align="center" justify="center">
                        <Avatar size="2xl" name={userProfile.name} src={userProfile.avatar} mb={4} />
                        <Button leftIcon={<FiUpload />} variant="outline">
                          Cambiar foto
                        </Button>
                        <Text fontSize="sm" color="gray.500" mt={2}>
                          Formatos permitidos: JPG, PNG (máx. 2MB)
                        </Text>
                      </VStack>
                    </SimpleGrid>
                  </CardBody>
                  <CardFooter justify="flex-end">
                    <Button colorScheme="blue" leftIcon={<FiSave />} onClick={handleSaveSettings}>
                      Guardar cambios
                    </Button>
                  </CardFooter>
                </Card>

                <Card>
                  <CardHeader>
                    <Heading size="md">Cambiar contraseña</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <FormControl>
                        <FormLabel>Contraseña actual</FormLabel>
                        <HStack>
                          <Input 
                            type={showCurrentPassword ? "text" : "password"} 
                            placeholder="Ingresa tu contraseña actual"
                          />
                          <IconButton
                            icon={showCurrentPassword ? <FiEyeOff /> : <FiEye />}
                            onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                            aria-label={showCurrentPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                          />
                        </HStack>
                      </FormControl>
                      <FormControl>
                        <FormLabel>Nueva contraseña</FormLabel>
                        <HStack>
                          <Input 
                            type={showNewPassword ? "text" : "password"} 
                            placeholder="Ingresa tu nueva contraseña"
                          />
                          <IconButton
                            icon={showNewPassword ? <FiEyeOff /> : <FiEye />}
                            onClick={() => setShowNewPassword(!showNewPassword)}
                            aria-label={showNewPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                          />
                        </HStack>
                      </FormControl>
                      <FormControl>
                        <FormLabel>Confirmar nueva contraseña</FormLabel>
                        <HStack>
                          <Input 
                            type={showConfirmPassword ? "text" : "password"} 
                            placeholder="Confirma tu nueva contraseña"
                          />
                          <IconButton
                            icon={showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            aria-label={showConfirmPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                          />
                        </HStack>
                      </FormControl>
                    </VStack>
                  </CardBody>
                  <CardFooter justify="flex-end">
                    <Button colorScheme="blue" leftIcon={<FiLock />} onClick={handleSaveSettings}>
                      Actualizar contraseña
                    </Button>
                  </CardFooter>
                </Card>
              </VStack>
            </TabPanel>

            {/* Pestaña de Notificaciones */}
            <TabPanel p={0}>
              <Card>
                <CardHeader>
                  <Heading size="md">Preferencias de Notificación</Heading>
                  <Text color="gray.500" mt={1}>
                    Controla cómo y cuándo recibes notificaciones
                  </Text>
                </CardHeader>
                <CardBody>
                  <VStack spacing={6} align="stretch">
                    <FormControl display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <FormLabel mb={0} fontWeight="medium">Notificaciones por correo electrónico</FormLabel>
                        <Text color="gray.500" fontSize="sm">Recibe actualizaciones importantes por correo</Text>
                      </Box>
                      <Switch isChecked={notificationSettings.emailNotifications} />
                    </FormControl>

                    <FormControl display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <FormLabel mb={0} fontWeight="medium">Notificaciones push</FormLabel>
                        <Text color="gray.500" fontSize="sm">Recibe notificaciones en tiempo real</Text>
                      </Box>
                      <Switch isChecked={notificationSettings.pushNotifications} />
                    </FormControl>

                    <FormControl display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <FormLabel mb={0} fontWeight="medium">Correos de marketing</FormLabel>
                        <Text color="gray.500" fontSize="sm">Recibe ofertas y actualizaciones de productos</Text>
                      </Box>
                      <Switch isChecked={notificationSettings.marketingEmails} />
                    </FormControl>

                    <FormControl display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <FormLabel mb={0} fontWeight="medium">Alertas de seguridad</FormLabel>
                        <Text color="gray.500" fontSize="sm">Recibe alertas sobre actividad sospechosa</Text>
                      </Box>
                      <Switch isChecked={notificationSettings.securityAlerts} />
                    </FormControl>

                    <FormControl display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <FormLabel mb={0} fontWeight="medium">Actualizaciones de propiedades</FormLabel>
                        <Text color="gray.500" fontSize="sm">Recibe notificaciones sobre propiedades guardadas</Text>
                      </Box>
                      <Switch isChecked={notificationSettings.propertyUpdates} />
                    </FormControl>
                  </VStack>
                </CardBody>
                <CardFooter justify="flex-end">
                  <Button colorScheme="blue" leftIcon={<FiSave />} onClick={handleSaveSettings}>
                    Guardar preferencias
                  </Button>
                </CardFooter>
              </Card>
            </TabPanel>

            {/* Pestaña de Seguridad */}
            <TabPanel p={0}>
              <VStack spacing={6} align="stretch">
                <Card>
                  <CardHeader>
                    <Heading size="md">Seguridad de la Cuenta</Heading>
                    <Text color="gray.500" mt={1}>
                      Protege tu cuenta con configuraciones de seguridad avanzadas
                    </Text>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={6} align="stretch">
                      <FormControl display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                          <FormLabel mb={0} fontWeight="medium">Autenticación de dos factores (2FA)</FormLabel>
                          <Text color="gray.500" fontSize="sm">Añade una capa adicional de seguridad a tu cuenta</Text>
                        </Box>
                        <Switch isChecked={securitySettings.twoFactorAuth} />
                      </FormControl>

                      <FormControl display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                          <FormLabel mb={0} fontWeight="medium">Alertas de inicio de sesión</FormLabel>
                          <Text color="gray.500" fontSize="sm">Recibe notificaciones cuando se inicie sesión en tu cuenta</Text>
                        </Box>
                        <Switch isChecked={securitySettings.loginAlerts} />
                      </FormControl>

                      <Divider my={4} />

                      <Box>
                        <Text fontWeight="medium" mb={4}>Dispositivos conectados</Text>
                        <Table variant="simple">
                          <Thead>
                            <Tr>
                              <Th>Dispositivo</Th>
                              <Th>Sistema Operativo</Th>
                              <Th>Último uso</Th>
                              <Th>Estado</Th>
                              <Th>Acciones</Th>
                            </Tr>
                          </Thead>
                          <Tbody>
                            {securitySettings.deviceManagement.map((device) => (
                              <Tr key={device.id}>
                                <Td>{device.name}</Td>
                                <Td>{device.os}</Td>
                                <Td>{device.lastUsed}</Td>
                                <Td>
                                  {device.current ? (
                                    <Badge colorScheme="green">Activo</Badge>
                                  ) : (
                                    <Badge colorScheme="gray">Inactivo</Badge>
                                  )}
                                </Td>
                                <Td>
                                  <Button size="sm" variant="outline" colorScheme="red" isDisabled={device.current}>
                                    Cerrar sesión
                                  </Button>
                                </Td>
                              </Tr>
                            ))}
                          </Tbody>
                        </Table>
                      </Box>
                    </VStack>
                  </CardBody>
                  <CardFooter justify="flex-end">
                    <Button colorScheme="blue" leftIcon={<FiSave />} onClick={handleSaveSettings}>
                      Guardar configuración
                    </Button>
                  </CardFooter>
                </Card>

                <Card borderColor="red.200">
                  <CardHeader>
                    <Heading size="md" color="red.600">Zona de peligro</Heading>
                    <Text color="red.500" fontSize="sm">
                      Estas acciones son irreversibles. Ten cuidado.
                    </Text>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <Text fontWeight="medium">Eliminar mi cuenta</Text>
                        <Text color="gray.500" fontSize="sm">
                          Una vez que elimines tu cuenta, no hay vuelta atrás. Por favor, ten en cuenta que esta acción no se puede deshacer.
                        </Text>
                      </Box>
                      <Button 
                        colorScheme="red" 
                        variant="outline" 
                        leftIcon={<FiTrash2 />}
                        onClick={onOpen}
                        alignSelf="flex-start"
                      >
                        Eliminar mi cuenta
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>
              </VStack>
            </TabPanel>

            {/* Pestaña de Pagos */}
            <TabPanel p={0}>
              <Card>
                <CardHeader>
                  <Heading size="md">Métodos de Pago</Heading>
                  <Text color="gray.500" mt={1}>
                    Administra tus métodos de pago y facturación
                  </Text>
                </CardHeader>
                <CardBody>
                  <VStack spacing={6} align="stretch">
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      <Box>
                        <AlertTitle>Plan Actual: Premium</AlertTitle>
                        <AlertDescription>
                          Tu próxima factura de $49.99 se generará el 01/08/2023
                        </AlertDescription>
                      </Box>
                    </Alert>

                    <Box>
                      <Text fontWeight="medium" mb={4}>Tarjetas guardadas</Text>
                      <Card variant="outline" p={4} maxW="md">
                        <HStack>
                          <FiCreditCard size={24} />
                          <Box flex={1}>
                            <Text fontWeight="medium">Visa terminada en 4242</Text>
                            <Text color="gray.500" fontSize="sm">Vence 12/25</Text>
                          </Box>
                          <Button size="sm" variant="outline" colorScheme="blue">
                            Editar
                          </Button>
                        </HStack>
                      </Card>
                    </Box>

                    <Divider my={4} />

                    <Box>
                      <Text fontWeight="medium" mb={4}>Historial de facturación</Text>
                      <Table variant="simple">
                        <Thead>
                          <Tr>
                            <Th>Fecha</Th>
                            <Th>Descripción</Th>
                            <Th isNumeric>Monto</Th>
                            <Th>Estado</Th>
                            <Th>Acciones</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          <Tr>
                            <Td>15/06/2023</Td>
                            <Td>Suscripción Premium - Mensual</Td>
                            <Td isNumeric>$49.99</Td>
                            <Td><Badge colorScheme="green">Pagado</Badge></Td>
                            <Td>
                              <Button size="sm" variant="link" colorScheme="blue">
                                Ver factura
                              </Button>
                            </Td>
                          </Tr>
                          <Tr>
                            <Td>15/05/2023</Td>
                            <Td>Suscripción Premium - Mensual</Td>
                            <Td isNumeric>$49.99</Td>
                            <Td><Badge colorScheme="green">Pagado</Badge></Td>
                            <Td>
                              <Button size="sm" variant="link" colorScheme="blue">
                                Ver factura
                              </Button>
                            </Td>
                          </Tr>
                        </Tbody>
                      </Table>
                    </Box>
                  </VStack>
                </CardBody>
                <CardFooter justify="flex-end">
                  <Button leftIcon={<FiPlus />} colorScheme="blue">
                    Añadir método de pago
                  </Button>
                </CardFooter>
              </Card>
            </TabPanel>

            {/* Pestaña de Datos */}
            <TabPanel p={0}>
              <VStack spacing={6} align="stretch">
                <Card>
                  <CardHeader>
                    <Heading size="md">Exportar datos</Heading>
                    <Text color="gray.500" mt={1}>
                      Descarga una copia de tus datos personales
                    </Text>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Text>
                        Puedes solicitar un archivo con los datos de tu cuenta, incluyendo tu perfil, 
                        preferencias y otra información que hayas proporcionado.
                      </Text>
                      <Box bg="blue.50" p={4} borderRadius="md" borderLeft="4px" borderColor="blue.500">
                        <HStack>
                          <FiInfo size={20} color="#3182ce" />
                          <Text color="blue.800">
                            El archivo de exportación incluirá todos tus datos en formato JSON. 
                            El proceso puede tardar unos minutos en completarse.
                          </Text>
                        </HStack>
                      </Box>
                    </VStack>
                  </CardBody>
                  <CardFooter>
                    <Button 
                      leftIcon={<FiDownload />} 
                      colorScheme="blue"
                      onClick={handleExportData}
                    >
                      Exportar mis datos
                    </Button>
                  </CardFooter>
                </Card>

                <Card>
                  <CardHeader>
                    <Heading size="md">Límites de almacenamiento</Heading>
                    <Text color="gray.500" mt={1}>
                      Espacio utilizado en tu cuenta
                    </Text>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Box>
                            <HStack justify="space-between" mb={2}>
                              <Text fontWeight="medium">Espacio utilizado</Text>
                              <Text>1.2 GB de 10 GB (12% usado)</Text>
                            </HStack>
                            <Progress value={12} size="sm" colorScheme="blue" borderRadius="full" />
                          </Box>
                          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={4}>
                            <Box>
                              <Text>Fotos</Text>
                              <Progress value={65} size="xs" colorScheme="green" borderRadius="full" mt={1} />
                              <Text fontSize="sm" color="gray.500">650 MB</Text>
                            </Box>
                            <Box>
                              <Text>Documentos</Text>
                              <Progress value={25} size="xs" colorScheme="blue" borderRadius="full" mt={1} />
                              <Text fontSize="sm" color="gray.500">250 MB</Text>
                            </Box>
                            <Box>
                              <Text>Correos electrónicos</Text>
                              <Progress value={10} size="xs" colorScheme="purple" borderRadius="full" mt={1} />
                              <Text fontSize="sm" color="gray.500">100 MB</Text>
                            </Box>
                            <Box>
                              <Text>Otros</Text>
                              <Progress value={20} size="xs" colorScheme="orange" borderRadius="full" mt={1} />
                              <Text fontSize="sm" color="gray.500">200 MB</Text>
                            </Box>
                          </SimpleGrid>
                        </VStack>
                      </CardBody>
                      <CardFooter>
                        <Button leftIcon={<FiPlus />} colorScheme="blue" variant="outline">
                          Actualizar plan
                        </Button>
                      </CardFooter>
                    </Card>
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </VStack>

          {/* Modal de confirmación para eliminar cuenta */}
          <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent>
              <ModalHeader>¿Estás seguro de que deseas eliminar tu cuenta?</ModalHeader>
              <ModalCloseButton />
              <ModalBody>
                <Text>Esta acción no se puede deshacer. Todos tus datos se eliminarán permanentemente.</Text>
              </ModalBody>
              <ModalFooter>
                <Button variant="ghost" mr={3} onClick={onClose}>
                  Cancelar
                </Button>
                <Button colorScheme="red" onClick={handleDeleteAccount}>
                  Confirmar eliminación
                </Button>
              </ModalFooter>
            </ModalContent>
          </Modal>
        </Box>
      );
    };
    
    export default Settings;
