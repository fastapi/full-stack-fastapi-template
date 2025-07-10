import React, { useState, useEffect } from 'react';
import { Box, Flex, Heading, Text, Button, Badge, Input, Select } from '@chakra-ui/react';
import { FiHome, FiMapPin, FiDollarSign, FiUser, FiPhone, FiMail, FiCalendar, FiEdit, FiTrash, FiPlus, FiFilter, FiDownload, FiEye, FiCamera } from 'react-icons/fi';

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
  commission_rate?: number; // Para propietarios terceros
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
  type: 'apartment' | 'house' | 'commercial' | 'land' | 'office';
  status: 'available' | 'reserved' | 'sold' | 'rented' | 'under_construction';
  price: Price;
  area: number; // m²
  bedrooms?: number;
  bathrooms?: number;
  parking_spaces?: number;
  floor?: number;
  stratum: number; // Estrato socioeconomico
  address: string;
  neighborhood: string;
  city: string;
  department: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  owner: Owner;
  agent_id: string;
  images: string[];
  features: string[];
  created_at: string;
  updated_at: string;
  visits_count: number;
  inquiries_count: number;
  last_activity: string;
  construction_year?: number;
  property_tax?: number; // Predial anual
  admin_fee?: number; // Administración mensual
}

// Tasas de cambio ficticias (en una implementación real vendrían de una API)
const EXCHANGE_RATES = {
  USD_TO_COP: 4150,
  EUR_TO_COP: 4580,
  USD_TO_EUR: 0.91,
};

export function PropertyCRM() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [filteredProperties, setFilteredProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'map'>('grid');
  const [currentCurrency, setCurrentCurrency] = useState<'cop' | 'usd' | 'eur'>('cop');
  
  // Filtros
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    priceMin: '',
    priceMax: '',
    city: '',
    neighborhood: '',
    bedrooms: '',
    bathrooms: '',
    owner_type: '',
    agent: ''
  });

  // Form data para crear/editar propiedades
  const [formData, setFormData] = useState<Partial<Property & { owner: Partial<Owner> }>>({
    title: '',
    description: '',
    type: 'apartment',
    status: 'available',
    price: { cop: 0, usd: 0, eur: 0 },
    area: 0,
    bedrooms: 0,
    bathrooms: 0,
    parking_spaces: 0,
    stratum: 1,
    address: '',
    neighborhood: '',
    city: '',
    department: '',
    features: [],
    owner: {
      type: 'own',
      name: '',
      email: '',
      phone: '',
      document_type: 'CC',
      document_number: ''
    }
  });

  // Función para convertir precios
  const convertPrice = (price: Price, toCurrency: 'cop' | 'usd' | 'eur'): number => {
    switch (toCurrency) {
      case 'cop':
        return price.cop;
      case 'usd':
        return price.usd || (price.cop / EXCHANGE_RATES.USD_TO_COP);
      case 'eur':
        return price.eur || (price.cop / EXCHANGE_RATES.EUR_TO_COP);
      default:
        return price.cop;
    }
  };

  // Función para formatear precio
  const formatPrice = (price: Price, currency: 'cop' | 'usd' | 'eur'): string => {
    const amount = convertPrice(price, currency);
    const symbols = { cop: '$', usd: 'US$', eur: '€' };
    
    return `${symbols[currency]} ${amount.toLocaleString('es-CO', {
      minimumFractionDigits: currency === 'cop' ? 0 : 2,
      maximumFractionDigits: currency === 'cop' ? 0 : 2
    })}`;
  };

  // Datos de ejemplo
  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      const mockProperties: Property[] = [
        {
          id: '1',
          title: 'Apartamento de Lujo en Zona Rosa',
          description: 'Hermoso apartamento completamente remodelado con vista panorámica de la ciudad.',
          type: 'apartment',
          status: 'available',
          price: { cop: 850000000, usd: 205000, eur: 186000 },
          area: 120,
          bedrooms: 3,
          bathrooms: 2,
          parking_spaces: 2,
          floor: 15,
          stratum: 6,
          address: 'Carrera 15 #93-47',
          neighborhood: 'Zona Rosa',
          city: 'Bogotá',
          department: 'Cundinamarca',
          owner: {
            id: 'owner1',
            type: 'third_party',
            name: 'María González',
            email: 'maria.gonzalez@email.com',
            phone: '+57 300 123 4567',
            document_type: 'CC',
            document_number: '52123456',
            commission_rate: 3
          },
          agent_id: 'agent1',
          images: ['url1', 'url2', 'url3'],
          features: ['Balcón', 'Aire Acondicionado', 'Cocina Integral', 'Closets', 'Portería 24h'],
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-12-20T15:30:00Z',
          visits_count: 25,
          inquiries_count: 8,
          last_activity: '2024-12-19T14:20:00Z',
          construction_year: 2018,
          property_tax: 2400000,
          admin_fee: 320000
        },
        {
          id: '2',
          title: 'Casa Campestre en La Calera',
          description: 'Espectacular casa con amplio jardín, perfecta para familias.',
          type: 'house',
          status: 'reserved',
          price: { cop: 1200000000, usd: 289000, eur: 262000 },
          area: 250,
          bedrooms: 4,
          bathrooms: 3,
          parking_spaces: 3,
          stratum: 5,
          address: 'Vereda El Salitre, Km 2',
          neighborhood: 'El Salitre',
          city: 'La Calera',
          department: 'Cundinamarca',
          owner: {
            id: 'owner2',
            type: 'own',
            name: 'GENIUS INDUSTRIES',
            email: 'propiedades@geniusindustries.com',
            phone: '+57 1 234 5678',
            document_type: 'NIT',
            document_number: '900123456-1'
          },
          agent_id: 'agent2',
          images: ['url4', 'url5'],
          features: ['Jardín', 'BBQ', 'Chimenea', 'Terraza', 'Zona de Juegos'],
          created_at: '2024-02-10T08:00:00Z',
          updated_at: '2024-12-18T12:00:00Z',
          visits_count: 15,
          inquiries_count: 12,
          last_activity: '2024-12-18T11:45:00Z',
          construction_year: 2020,
          property_tax: 3200000,
          admin_fee: 0
        }
      ];
      setProperties(mockProperties);
      setFilteredProperties(mockProperties);
      setLoading(false);
    }, 1000);
  }, []);

  // Aplicar filtros
  useEffect(() => {
    let filtered = properties.filter(property => {
      return (
        (!filters.type || property.type === filters.type) &&
        (!filters.status || property.status === filters.status) &&
        (!filters.city || property.city.toLowerCase().includes(filters.city.toLowerCase())) &&
        (!filters.neighborhood || property.neighborhood.toLowerCase().includes(filters.neighborhood.toLowerCase())) &&
        (!filters.bedrooms || property.bedrooms === parseInt(filters.bedrooms)) &&
        (!filters.bathrooms || property.bathrooms === parseInt(filters.bathrooms)) &&
        (!filters.owner_type || property.owner.type === filters.owner_type) &&
        (!filters.priceMin || convertPrice(property.price, currentCurrency) >= parseFloat(filters.priceMin)) &&
        (!filters.priceMax || convertPrice(property.price, currentCurrency) <= parseFloat(filters.priceMax))
      );
    });
    setFilteredProperties(filtered);
  }, [filters, properties, currentCurrency]);

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

  const openCreateModal = () => {
    setIsEditing(false);
    setSelectedProperty(null);
    setFormData({
      title: '',
      description: '',
      type: 'apartment',
      status: 'available',
      price: { cop: 0, usd: 0, eur: 0 },
      area: 0,
      bedrooms: 0,
      bathrooms: 0,
      parking_spaces: 0,
      stratum: 1,
      address: '',
      neighborhood: '',
      city: '',
      department: '',
      features: [],
      owner: {
        type: 'own',
        name: '',
        email: '',
        phone: '',
        document_type: 'CC',
        document_number: ''
      }
    });
    setIsModalOpen(true);
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
            {formatPrice(property.price, currentCurrency)}
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
            {property.neighborhood}, {property.city}
          </Text>
        </div>

        {/* Propietario */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
          <FiUser size={14} color="#666" />
          <Text fontSize="sm" color="#666">
            {property.owner.type === 'own' ? 'Propio' : 'Tercero'}: {property.owner.name}
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
          <span>{property.visits_count} visitas</span>
          <span>{property.inquiries_count} consultas</span>
          <span>Estrato {property.stratum}</span>
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
          >
            <FiEye size={14} />
            Ver Detalles
          </button>
          <button
            style={{
              background: '#f7fafc',
              color: '#4a5568',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              padding: '8px',
              cursor: 'pointer'
            }}
          >
            <FiEdit size={14} />
          </button>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <Box p={6}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Text>Cargando propiedades...</Text>
        </div>
      </Box>
    );
  }

  return (
    <Box p={6}>
      {/* Analytics Overview */}
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
            <Text fontSize="3xl" fontWeight="bold" mt={2}>{properties.length}</Text>
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
              {properties.filter(p => p.status === 'available').length}
            </Text>
            <Text fontSize="xs" opacity={0.8} mt={1}>
              {((properties.filter(p => p.status === 'available').length / properties.length) * 100).toFixed(1)}% del total
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
            <Text fontSize="2xl" fontWeight="bold" mt={2}>
              {formatPrice(
                {
                  cop: properties.reduce((sum, p) => sum + p.price.cop, 0),
                  usd: properties.reduce((sum, p) => sum + convertPrice(p.price, 'usd'), 0),
                  eur: properties.reduce((sum, p) => sum + convertPrice(p.price, 'eur'), 0)
                },
                currentCurrency
              )}
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
            <Text fontSize="2xl" fontWeight="bold" mt={2}>
              {formatPrice(
                {
                  cop: properties.reduce((sum, p) => sum + p.price.cop, 0) / properties.length,
                  usd: properties.reduce((sum, p) => sum + convertPrice(p.price, 'usd'), 0) / properties.length,
                  eur: properties.reduce((sum, p) => sum + convertPrice(p.price, 'eur'), 0) / properties.length
                },
                currentCurrency
              )}
            </Text>
            <Text fontSize="xs" opacity={0.8} mt={1}>Por propiedad</Text>
          </div>

          {/* Recent Activity */}
          <div style={{
            background: 'linear-gradient(135deg, #38b2ac 0%, #319795 100%)',
            color: 'white',
            padding: '20px',
            borderRadius: '12px',
            textAlign: 'center'
          }}>
            <Text fontSize="sm" opacity={0.9}>Actividad Reciente</Text>
            <Text fontSize="3xl" fontWeight="bold" mt={2}>
              {properties.reduce((sum, p) => sum + p.visits_count, 0)}
            </Text>
            <Text fontSize="xs" opacity={0.8} mt={1}>Total visitas</Text>
          </div>

          {/* Performance Metrics */}
          <div style={{
            background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
            color: 'white',
            padding: '20px',
            borderRadius: '12px',
            textAlign: 'center'
          }}>
            <Text fontSize="sm" opacity={0.9}>Consultas</Text>
            <Text fontSize="3xl" fontWeight="bold" mt={2}>
              {properties.reduce((sum, p) => sum + p.inquiries_count, 0)}
            </Text>
            <Text fontSize="xs" opacity={0.8} mt={1}>
              Tasa conversión: {(
                (properties.reduce((sum, p) => sum + p.inquiries_count, 0) / 
                properties.reduce((sum, p) => sum + p.visits_count, 0)) * 100
              ).toFixed(1)}%
            </Text>
          </div>
        </div>

        {/* Property Distribution */}
        <Box mt={6}>
          <Heading size="sm" mb={3} color="#1a202c">
            Distribución por Tipo y Estado
          </Heading>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            {/* Por Tipo */}
            <div style={{ background: '#f7fafc', padding: '16px', borderRadius: '8px' }}>
              <Text fontSize="sm" fontWeight="600" mb={2}>Por Tipo</Text>
              {['apartment', 'house', 'commercial', 'land', 'office'].map(type => {
                const count = properties.filter(p => p.type === type).length;
                const percentage = (count / properties.length) * 100;
                return count > 0 ? (
                  <div key={type} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <Text fontSize="xs">{getTypeLabel(type)}</Text>
                    <Text fontSize="xs" fontWeight="600">{count} ({percentage.toFixed(1)}%)</Text>
                  </div>
                ) : null;
              })}
            </div>

            {/* Por Estado */}
            <div style={{ background: '#f7fafc', padding: '16px', borderRadius: '8px' }}>
              <Text fontSize="sm" fontWeight="600" mb={2}>Por Estado</Text>
              {['available', 'reserved', 'sold', 'rented', 'under_construction'].map(status => {
                const count = properties.filter(p => p.status === status).length;
                const percentage = (count / properties.length) * 100;
                return count > 0 ? (
                  <div key={status} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <Text fontSize="xs">{getStatusLabel(status)}</Text>
                    <Text fontSize="xs" fontWeight="600">{count} ({percentage.toFixed(1)}%)</Text>
                  </div>
                ) : null;
              })}
            </div>

            {/* Por Ciudad */}
            <div style={{ background: '#f7fafc', padding: '16px', borderRadius: '8px' }}>
              <Text fontSize="sm" fontWeight="600" mb={2}>Por Ciudad</Text>
              {Array.from(new Set(properties.map(p => p.city))).map(city => {
                const count = properties.filter(p => p.city === city).length;
                const avgPrice = properties
                  .filter(p => p.city === city)
                  .reduce((sum, p) => sum + convertPrice(p.price, currentCurrency), 0) / count;
                return (
                  <div key={city} style={{ marginBottom: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Text fontSize="xs">{city}</Text>
                      <Text fontSize="xs" fontWeight="600">{count}</Text>
                    </div>
                    <Text fontSize="xs" color="#666">
                      Promedio: {formatPrice({ cop: avgPrice, usd: avgPrice, eur: avgPrice }, currentCurrency)}
                    </Text>
                  </div>
                );
              })}
            </div>
          </div>
        </Box>
      </Box>

      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg" color="text">
            CRM de Propiedades
          </Heading>
          <Text color="text.muted" mt={1}>
            Gestión completa de propiedades inmobiliarias
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
              value={filters.type}
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
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
            <Text fontSize="sm" fontWeight="500" mb={2}>Barrio</Text>
            <Input
              value={filters.neighborhood}
              onChange={(e) => setFilters({ ...filters, neighborhood: e.target.value })}
              placeholder="Buscar barrio..."
              size="sm"
            />
          </div>

          <div>
            <Text fontSize="sm" fontWeight="500" mb={2}>Propietario</Text>
            <Select
              value={filters.owner_type}
              onChange={(e) => setFilters({ ...filters, owner_type: e.target.value })}
              size="sm"
            >
              <option value="">Todos</option>
              <option value="own">Propias</option>
              <option value="third_party">Terceros</option>
            </Select>
          </div>

          <Button leftIcon={<FiFilter />} colorScheme="blue" size="sm">
            Aplicar Filtros
          </Button>
        </div>
      </Box>

      {/* Estadísticas rápidas */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px',
        marginBottom: '24px'
      }}>
        <Box bg="bg.surface" p={5} borderRadius="12px" boxShadow="0 2px 4px rgba(0,0,0,0.05)" border="1px" borderColor="border">
          <Text fontSize="sm" color="text.muted">Total Propiedades</Text>
          <Text fontSize="2xl" fontWeight="700" color="text">{properties.length}</Text>
        </Box>
        <Box bg="bg.surface" p={5} borderRadius="12px" boxShadow="0 2px 4px rgba(0,0,0,0.05)" border="1px" borderColor="border">
          <Text fontSize="sm" color="text.muted">Disponibles</Text>
          <Text fontSize="2xl" fontWeight="700" color="green.400">
            {properties.filter(p => p.status === 'available').length}
          </Text>
        </Box>
        <Box bg="bg.surface" p={5} borderRadius="12px" boxShadow="0 2px 4px rgba(0,0,0,0.05)" border="1px" borderColor="border">
          <Text fontSize="sm" color="text.muted">Vendidas/Arrendadas</Text>
          <Text fontSize="2xl" fontWeight="700" color="blue.400">
            {properties.filter(p => p.status === 'sold' || p.status === 'rented').length}
          </Text>
        </Box>
        <Box bg="bg.surface" p={5} borderRadius="12px" boxShadow="0 2px 4px rgba(0,0,0,0.05)" border="1px" borderColor="border">
          <Text fontSize="sm" color="text.muted">Valor Inventario</Text>
          <Text fontSize="2xl" fontWeight="700" color="purple.400">
            {formatPrice(
              { cop: properties.reduce((sum, p) => sum + p.price.cop, 0), usd: 0, eur: 0 },
              currentCurrency
            )}
          </Text>
        </Box>
      </div>

      {/* Lista de propiedades */}
      <Box bg="bg.surface" borderRadius="12px" p={6} boxShadow="0 2px 8px rgba(0,0,0,0.1)" border="1px" borderColor="border">
        <Flex justify="space-between" align="center" mb={4}>
          <Text fontSize="lg" fontWeight="600">
            Propiedades ({filteredProperties.length})
          </Text>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setViewMode('grid')}
              style={{
                padding: '8px',
                border: viewMode === 'grid' ? '2px solid #3182ce' : '1px solid #e2e8f0',
                borderRadius: '6px',
                background: viewMode === 'grid' ? '#ebf8ff' : '#fff',
                cursor: 'pointer'
              }}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              style={{
                padding: '8px',
                border: viewMode === 'list' ? '2px solid #3182ce' : '1px solid #e2e8f0',
                borderRadius: '6px',
                background: viewMode === 'list' ? '#ebf8ff' : '#fff',
                cursor: 'pointer'
              }}
            >
              Lista
            </button>
          </div>
        </Flex>

        {filteredProperties.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <FiHome size={48} color="#ccc" />
            <Text color="#666" mt={4}>No se encontraron propiedades</Text>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: viewMode === 'grid' ? 'repeat(auto-fill, minmax(350px, 1fr))' : '1fr',
            gap: '20px'
          }}>
            {filteredProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </Box>
    </Box>
  );
} 
