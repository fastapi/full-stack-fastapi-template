import React, { useState, useEffect } from 'react';
import { Box, Flex, Heading, Text, Button, Badge, Input, Select } from '@chakra-ui/react';
import { FiHome, FiMapPin, FiDollarSign, FiUser, FiPhone, FiMail, FiCalendar, FiEdit, FiTrash, FiPlus, FiFilter, FiDownload, FiEye, FiCamera, FiSave } from 'react-icons/fi';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { toaster } from '../../components/ui/toaster';

// Configuración de API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interfaces para el CRM de propiedades
interface Owner {
  id: string;
  type: 'own' | 'third_party';
  name: string;
  email: string;
  phone: string;
  document_type: string;
  document_number: string;
  address?: string;
  commission_rate?: number;
}

interface Price {
  cop: number;
  usd: number;
  eur: number;
}

interface Property {
  id: string;
  title: string;
  description: string;
  property_type: 'apartment' | 'house' | 'commercial' | 'land' | 'office';
  status: 'available' | 'reserved' | 'sold' | 'rented' | 'under_construction';
  price: number;
  currency: string;
  area: number;
  bedrooms?: number;
  bathrooms?: number;
  parking_spaces?: number;
  address: string;
  city: string;
  state: string;
  country: string;
  zip_code?: string;
  features: string[];
  amenities: string[];
  images: string[];
  latitude?: number;
  longitude?: number;
  year_built?: number;
  condition?: string;
  created_at: string;
  updated_at: string;
  views: number;
  favorites: number;
  visits: number;
}

// API Functions
const propertyAPI = {
  getProperties: async (params: any = {}) => {
    const response = await api.get('/properties', { params });
    return response.data;
  },
  
  getProperty: async (id: string) => {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  },
  
  createProperty: async (propertyData: any) => {
    const response = await api.post('/properties', propertyData);
    return response.data;
  },
  
  updateProperty: async (id: string, propertyData: any) => {
    const response = await api.patch(`/properties/${id}`, propertyData);
    return response.data;
  },
  
  deleteProperty: async (id: string) => {
    const response = await api.delete(`/properties/${id}`);
    return response.data;
  },
  
  getAnalytics: async () => {
    const response = await api.get('/properties/analytics/dashboard');
    return response.data.data;
  }
};

// Tasas de cambio ficticias (en una implementación real vendrían de una API)
const EXCHANGE_RATES = {
  USD_TO_COP: 4150,
  EUR_TO_COP: 4580,
  USD_TO_EUR: 0.91,
};

export function PropertyCRM() {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'map'>('grid');
  const [currentCurrency, setCurrentCurrency] = useState<'cop' | 'usd' | 'eur'>('cop');
  const toast = toaster.create;
  const queryClient = useQueryClient();
  
  // Filtros
  const [filters, setFilters] = useState({
    property_type: '',
    status: '',
    priceMin: '',
    priceMax: '',
    city: '',
    skip: 0,
    limit: 20
  });

  // Form data para crear/editar propiedades
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    property_type: 'apartment',
    status: 'available',
    price: 0,
    currency: 'COP',
    area: 0,
    bedrooms: 0,
    bathrooms: 0,
    parking_spaces: 0,
    address: '',
    city: '',
    state: '',
    country: 'Colombia',
    zip_code: '',
    features: [],
    amenities: [],
    images: [],
    year_built: new Date().getFullYear(),
    condition: 'good'
  });

  // Query para obtener propiedades
  const { data: propertiesData, isLoading, error, refetch } = useQuery({
    queryKey: ['properties', filters],
    queryFn: () => propertyAPI.getProperties({
      skip: filters.skip,
      limit: filters.limit,
      property_type: filters.property_type || undefined,
      status: filters.status || undefined,
      min_price: filters.priceMin ? parseFloat(filters.priceMin) : undefined,
      max_price: filters.priceMax ? parseFloat(filters.priceMax) : undefined,
      city: filters.city || undefined
    }),
    staleTime: 30000, // Cache por 30 segundos
  });

  // Query para analytics
  const { data: analytics } = useQuery({
    queryKey: ['properties-analytics'],
    queryFn: propertyAPI.getAnalytics,
    staleTime: 60000, // Cache por 1 minuto
  });

  // Mutación para crear propiedad
  const createPropertyMutation = useMutation({
    mutationFn: propertyAPI.createProperty,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] });
      queryClient.invalidateQueries({ queryKey: ['properties-analytics'] });
      toast({
        title: 'Propiedad creada',
        description: 'La propiedad se ha creado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al crear la propiedad',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Mutación para actualizar propiedad
  const updatePropertyMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => 
      propertyAPI.updateProperty(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] });
      queryClient.invalidateQueries({ queryKey: ['properties-analytics'] });
      toast({
        title: 'Propiedad actualizada',
        description: 'La propiedad se ha actualizado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      setIsModalOpen(false);
      setSelectedProperty(null);
      resetForm();
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al actualizar la propiedad',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Mutación para eliminar propiedad
  const deletePropertyMutation = useMutation({
    mutationFn: propertyAPI.deleteProperty,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] });
      queryClient.invalidateQueries({ queryKey: ['properties-analytics'] });
      toast({
        title: 'Propiedad eliminada',
        description: 'La propiedad se ha eliminado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al eliminar la propiedad',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const properties = propertiesData?.data || [];
  const totalProperties = propertiesData?.total || 0;

  // Función para convertir precios
  const convertPrice = (price: number, currency: string, toCurrency: 'cop' | 'usd' | 'eur'): number => {
    let priceInCOP = price;
    
    // Convertir a COP primero si no está en COP
    if (currency === 'USD') {
      priceInCOP = price * EXCHANGE_RATES.USD_TO_COP;
    } else if (currency === 'EUR') {
      priceInCOP = price * EXCHANGE_RATES.EUR_TO_COP;
    }
    
    // Convertir de COP a la moneda objetivo
    switch (toCurrency) {
      case 'cop':
        return priceInCOP;
      case 'usd':
        return priceInCOP / EXCHANGE_RATES.USD_TO_COP;
      case 'eur':
        return priceInCOP / EXCHANGE_RATES.EUR_TO_COP;
      default:
        return priceInCOP;
    }
  };

  // Función para formatear precio
  const formatPrice = (price: number, currency: string): string => {
    const convertedPrice = convertPrice(price, currency, currentCurrency);
    const symbols = { cop: '$', usd: 'US$', eur: '€' };
    
    return `${symbols[currentCurrency]} ${convertedPrice.toLocaleString('es-CO', {
      minimumFractionDigits: currentCurrency === 'cop' ? 0 : 2,
      maximumFractionDigits: currentCurrency === 'cop' ? 0 : 2
    })}`;
  };

  const getStatusColor = (status: string) => {
    const colors = {
      available: 'green',
      reserved: 'orange',
      sold: 'blue',
      rented: 'purple',
      under_construction: 'gray'
    };
    return colors[status as keyof typeof colors] || 'gray';
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      available: 'Disponible',
      reserved: 'Reservada',
      sold: 'Vendida',
      rented: 'Arrendada',
      under_construction: 'En Construcción'
    };
    return labels[status as keyof typeof labels] || status;
  };

  const getTypeLabel = (type: string) => {
    const labels = {
      apartment: 'Apartamento',
      house: 'Casa',
      commercial: 'Comercial',
      land: 'Lote',
      office: 'Oficina'
    };
    return labels[type as keyof typeof labels] || type;
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      property_type: 'apartment',
      status: 'available',
      price: 0,
      currency: 'COP',
      area: 0,
      bedrooms: 0,
      bathrooms: 0,
      parking_spaces: 0,
      address: '',
      city: '',
      state: '',
      country: 'Colombia',
      zip_code: '',
      features: [],
      amenities: [],
      images: [],
      year_built: new Date().getFullYear(),
      condition: 'good'
    });
  };

  const openCreateModal = () => {
    setIsEditing(false);
    setSelectedProperty(null);
    resetForm();
    setIsModalOpen(true);
  };

  const openEditModal = (property: Property) => {
    setIsEditing(true);
    setSelectedProperty(property);
    setFormData({
      title: property.title,
      description: property.description,
      property_type: property.property_type,
      status: property.status,
      price: property.price,
      currency: property.currency,
      area: property.area,
      bedrooms: property.bedrooms || 0,
      bathrooms: property.bathrooms || 0,
      parking_spaces: property.parking_spaces || 0,
      address: property.address,
      city: property.city,
      state: property.state,
      country: property.country,
      zip_code: property.zip_code || '',
      features: property.features,
      amenities: property.amenities,
      images: property.images,
      year_built: property.year_built || new Date().getFullYear(),
      condition: property.condition || 'good'
    });
    setIsModalOpen(true);
  };

  const handleSaveProperty = () => {
    if (isEditing && selectedProperty) {
      updatePropertyMutation.mutate({
        id: selectedProperty.id,
        data: formData
      });
    } else {
      createPropertyMutation.mutate(formData);
    }
  };

  const handleDeleteProperty = (propertyId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar esta propiedad?')) {
      deletePropertyMutation.mutate(propertyId);
    }
  };

  const PropertyCard = ({ property }: { property: Property }) => (
    <div style={{
      background: '#fff',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      overflow: 'hidden',
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'pointer'
    }}>
      {/* Imagen principal */}
      <div style={{
        height: '200px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        position: 'relative'
      }}>
        <FiCamera size={32} />
        <Badge
          colorScheme={getStatusColor(property.status)}
          style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            fontSize: '10px'
          }}
        >
          {getStatusLabel(property.status)}
        </Badge>
      </div>

      <div style={{ padding: '16px' }}>
        {/* Título y precio */}
        <div style={{ marginBottom: '12px' }}>
          <Text fontSize="lg" fontWeight="600" color="#1a202c" noOfLines={2}>
            {property.title}
          </Text>
          <Text fontSize="xl" fontWeight="700" color="#3182ce" marginTop="4px">
            {formatPrice(property.price, property.currency)}
          </Text>
        </div>

        {/* Detalles básicos */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '8px',
          marginBottom: '12px'
        }}>
          <div style={{ textAlign: 'center', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
            <Text fontSize="xs" color="#666">Área</Text>
            <Text fontSize="sm" fontWeight="600">{property.area}m²</Text>
          </div>
          {property.bedrooms && (
            <div style={{ textAlign: 'center', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
              <Text fontSize="xs" color="#666">Habitaciones</Text>
              <Text fontSize="sm" fontWeight="600">{property.bedrooms}</Text>
            </div>
          )}
          {property.bathrooms && (
            <div style={{ textAlign: 'center', padding: '8px', background: '#f7fafc', borderRadius: '6px' }}>
              <Text fontSize="xs" color="#666">Baños</Text>
              <Text fontSize="sm" fontWeight="600">{property.bathrooms}</Text>
            </div>
          )}
        </div>

        {/* Ubicación */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
          <FiMapPin size={14} color="#666" />
          <Text fontSize="sm" color="#666" noOfLines={1}>
            {property.city}, {property.state}
          </Text>
        </div>

        {/* Métricas */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          marginBottom: '16px',
          fontSize: '12px',
          color: '#666'
        }}>
          <span>{property.views} visitas</span>
          <span>{property.favorites} favoritos</span>
          <span>{getTypeLabel(property.property_type)}</span>
        </div>

        {/* Acciones */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            style={{
              flex: 1,
              background: '#3182ce',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 12px',
              fontSize: '14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
            onClick={() => openEditModal(property)}
          >
            <FiEye size={14} />
            Ver/Editar
          </button>
          <button
            style={{
              background: '#f7fafc',
              color: '#e53e3e',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              padding: '8px',
              cursor: 'pointer'
            }}
            onClick={() => handleDeleteProperty(property.id)}
          >
            <FiTrash size={14} />
          </button>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <Box p={6}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text>Cargando propiedades...</Text>
        </div>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={6}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text color="red.500">Error cargando propiedades</Text>
          <Button onClick={() => refetch()} mt={4}>
            Reintentar
          </Button>
        </div>
      </Box>
    );
  }

  return (
    <Box p={6}>
      {/* Analytics Overview */}
      {analytics && (
        <Box bg="bg.surface" p={6} borderRadius="12px" mb={6} boxShadow="0 2px 8px rgba(0,0,0,0.05)" border="1px" borderColor="border">
          <Heading size="md" mb={4} color="text">
            Dashboard de Analytics
          </Heading>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px'
          }}>
            {/* Total Properties */}
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '20px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Text fontSize="sm" opacity={0.9}>Total Propiedades</Text>
              <Text fontSize="3xl" fontWeight="bold" mt={2}>{analytics.total_properties}</Text>
              <Text fontSize="xs" opacity={0.8} mt={1}>Inventario activo</Text>
            </div>

            {/* Available Properties */}
            <div style={{
              background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
              color: 'white',
              padding: '20px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Text fontSize="sm" opacity={0.9}>Disponibles</Text>
              <Text fontSize="3xl" fontWeight="bold" mt={2}>
                {analytics.available_properties}
              </Text>
              <Text fontSize="xs" opacity={0.8} mt={1}>
                {analytics.total_properties > 0 ? 
                  ((analytics.available_properties / analytics.total_properties) * 100).toFixed(1) 
                  : 0}% del total
              </Text>
            </div>

            {/* Total Value */}
            <div style={{
              background: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
              color: 'white',
              padding: '20px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Text fontSize="sm" opacity={0.9}>Valor Total Inventario</Text>
              <Text fontSize="xl" fontWeight="bold" mt={2}>
                ${analytics.total_inventory_value.toLocaleString('es-CO')}
              </Text>
              <Text fontSize="xs" opacity={0.8} mt={1}>Valor de mercado</Text>
            </div>

            {/* Average Price */}
            <div style={{
              background: 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)',
              color: 'white',
              padding: '20px',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Text fontSize="sm" opacity={0.9}>Precio Promedio</Text>
              <Text fontSize="xl" fontWeight="bold" mt={2}>
                ${analytics.average_property_price.toLocaleString('es-CO')}
              </Text>
              <Text fontSize="xs" opacity={0.8} mt={1}>Por propiedad</Text>
            </div>
          </div>
        </Box>
      )}

      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg" color="text">
            CRM de Propiedades
          </Heading>
          <Text color="text.muted" mt={1}>
            Gestión completa de propiedades inmobiliarias - {totalProperties} propiedades
          </Text>
        </Box>
        <Flex gap={3}>
          <Select
            value={currentCurrency}
            onChange={(e) => setCurrentCurrency(e.target.value as 'cop' | 'usd' | 'eur')}
            size="sm"
            width="120px"
          >
            <option value="cop">COP ($)</option>
            <option value="usd">USD (US$)</option>
            <option value="eur">EUR (€)</option>
          </Select>
          <Button leftIcon={<FiDownload />} colorScheme="gray" size="sm">
            Exportar
          </Button>
          <Button leftIcon={<FiPlus />} colorScheme="blue" onClick={openCreateModal}>
            Nueva Propiedad
          </Button>
        </Flex>
      </Flex>

      {/* Filtros */}
      <Box bg="bg.surface" p={4} borderRadius="12px" mb={6} boxShadow="0 2px 4px rgba(0,0,0,0.05)" border="1px" borderColor="border">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '16px',
          alignItems: 'end'
        }}>
          <div>
            <Text fontSize="sm" fontWeight="500" mb={2}>Tipo de Propiedad</Text>
            <Select
              value={filters.property_type}
              onChange={(e) => setFilters({ ...filters, property_type: e.target.value })}
              size="sm"
            >
              <option value="">Todos los tipos</option>
              <option value="apartment">Apartamento</option>
              <option value="house">Casa</option>
              <option value="commercial">Comercial</option>
              <option value="land">Lote</option>
              <option value="office">Oficina</option>
            </Select>
          </div>

          <div>
            <Text fontSize="sm" fontWeight="500" mb={2}>Estado</Text>
            <Select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              size="sm"
            >
              <option value="">Todos los estados</option>
              <option value="available">Disponible</option>
              <option value="reserved">Reservada</option>
              <option value="sold">Vendida</option>
              <option value="rented">Arrendada</option>
              <option value="under_construction">En Construcción</option>
            </Select>
          </div>

          <div>
            <Text fontSize="sm" fontWeight="500" mb={2}>Ciudad</Text>
            <Input
              value={filters.city}
              onChange={(e) => setFilters({ ...filters, city: e.target.value })}
              placeholder="Buscar ciudad..."
              size="sm"
            />
          </div>

          <div>
            <Text fontSize="sm" fontWeight="500" mb={2}>Precio Mínimo</Text>
            <Input
              type="number"
              value={filters.priceMin}
              onChange={(e) => setFilters({ ...filters, priceMin: e.target.value })}
              placeholder="Precio mínimo"
              size="sm"
            />
          </div>

          <div>
            <Text fontSize="sm" fontWeight="500" mb={2}>Precio Máximo</Text>
            <Input
              type="number"
              value={filters.priceMax}
              onChange={(e) => setFilters({ ...filters, priceMax: e.target.value })}
              placeholder="Precio máximo"
              size="sm"
            />
          </div>

          <Button leftIcon={<FiFilter />} colorScheme="blue" size="sm">
            Filtrar
          </Button>
        </div>
      </Box>

      {/* Grid de Propiedades */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: '24px'
      }}>
        {properties.map((property: Property) => (
          <PropertyCard key={property.id} property={property} />
        ))}
      </div>

      {/* Modal para crear/editar propiedad */}
      {isModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <Heading size="md" mb={4}>
              {isEditing ? 'Editar Propiedad' : 'Nueva Propiedad'}
            </Heading>

            <div style={{ display: 'grid', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Título *</Text>
                  <Input
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="Título de la propiedad"
                  />
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Tipo *</Text>
                  <Select
                    value={formData.property_type}
                    onChange={(e) => setFormData({ ...formData, property_type: e.target.value as any })}
                  >
                    <option value="apartment">Apartamento</option>
                    <option value="house">Casa</option>
                    <option value="commercial">Comercial</option>
                    <option value="land">Lote</option>
                    <option value="office">Oficina</option>
                  </Select>
                </div>
              </div>

              <div>
                <Text fontSize="sm" fontWeight="500" mb={1}>Descripción</Text>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Descripción de la propiedad"
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Precio *</Text>
                  <Input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                    placeholder="Precio"
                  />
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Moneda</Text>
                  <Select
                    value={formData.currency}
                    onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  >
                    <option value="COP">COP</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                  </Select>
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Área (m²) *</Text>
                  <Input
                    type="number"
                    value={formData.area}
                    onChange={(e) => setFormData({ ...formData, area: parseFloat(e.target.value) || 0 })}
                    placeholder="Área"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Habitaciones</Text>
                  <Input
                    type="number"
                    value={formData.bedrooms}
                    onChange={(e) => setFormData({ ...formData, bedrooms: parseInt(e.target.value) || 0 })}
                    placeholder="Habitaciones"
                  />
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Baños</Text>
                  <Input
                    type="number"
                    value={formData.bathrooms}
                    onChange={(e) => setFormData({ ...formData, bathrooms: parseInt(e.target.value) || 0 })}
                    placeholder="Baños"
                  />
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Parqueaderos</Text>
                  <Input
                    type="number"
                    value={formData.parking_spaces}
                    onChange={(e) => setFormData({ ...formData, parking_spaces: parseInt(e.target.value) || 0 })}
                    placeholder="Parqueaderos"
                  />
                </div>
              </div>

              <div>
                <Text fontSize="sm" fontWeight="500" mb={1}>Dirección *</Text>
                <Input
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Dirección completa"
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Ciudad *</Text>
                  <Input
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    placeholder="Ciudad"
                  />
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Departamento *</Text>
                  <Input
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    placeholder="Departamento"
                  />
                </div>
                <div>
                  <Text fontSize="sm" fontWeight="500" mb={1}>Estado</Text>
                  <Select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                  >
                    <option value="available">Disponible</option>
                    <option value="reserved">Reservada</option>
                    <option value="sold">Vendida</option>
                    <option value="rented">Arrendada</option>
                    <option value="under_construction">En Construcción</option>
                  </Select>
                </div>
              </div>
            </div>

            <Flex gap={3} mt={6} justify="end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setIsModalOpen(false);
                  resetForm();
                }}
              >
                Cancelar
              </Button>
              <Button 
                colorScheme="blue" 
                leftIcon={<FiSave />}
                isLoading={createPropertyMutation.isPending || updatePropertyMutation.isPending}
                onClick={handleSaveProperty}
              >
                {isEditing ? 'Actualizar' : 'Crear'} Propiedad
              </Button>
            </Flex>
          </div>
        </div>
      )}
    </Box>
  );
} 
