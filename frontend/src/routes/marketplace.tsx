import React, { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { FiSearch, FiMapPin, FiHome, FiMaximize2, FiX, FiPhone, FiMail, FiDollarSign, FiCalendar, FiUser, FiImage, FiHeart, FiEye } from "react-icons/fi";
import { FaBath, FaBed } from "react-icons/fa";

interface Property {
  id: string;
  title: string;
  price: number;
  currency: string;
  location: string;
  address: string;
  propertyType: string;
  transactionType: string;
  bedrooms: number;
  bathrooms: number;
  area: number;
  yearBuilt: number;
  description: string;
  features: string[];
  images: string[];
  status: string;
  agentName: string;
  agentPhone: string;
  agentEmail: string;
  createdAt: string;
  views: number;
  isFavorite: boolean;
}

// Datos de ejemplo realistas hasta que se conecte al backend
const sampleProperties: Property[] = [
  {
    id: "1",
    title: "Casa Moderna en Zona Rosa",
    price: 850000000,
    currency: "COP",
    location: "Zona Rosa, Bogotá",
    address: "Carrera 13 #93-40, Zona Rosa",
    propertyType: "Casa",
    transactionType: "venta",
    bedrooms: 4,
    bathrooms: 3,
    area: 280,
    yearBuilt: 2019,
    description: "Espectacular casa moderna en el corazón de la Zona Rosa de Bogotá. Esta propiedad cuenta con acabados de lujo, amplios espacios, y una ubicación privilegiada cerca de los mejores restaurantes, centros comerciales y oficinas de la ciudad. Perfecta para familias que buscan comodidad y estilo de vida urbano.",
    features: [
      "Acabados de lujo",
      "Cocina integral con isla",
      "Terraza con jacuzzi",
      "Parqueadero para 2 carros",
      "Depósito privado",
      "Seguridad 24/7",
      "Gimnasio en el edificio",
      "Salón social"
    ],
    images: [
      "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "Carlos Martínez",
    agentPhone: "+57 316 682 7239",
    agentEmail: "carlos@geniusindustries.org",
    createdAt: "2024-01-15T10:00:00Z",
    views: 248,
    isFavorite: false
  },
  {
    id: "2",
    title: "Apartamento de Lujo en El Poblado",
    price: 650000000,
    currency: "COP",
    location: "El Poblado, Medellín",
    address: "Carrera 43A #16-38, El Poblado",
    propertyType: "Apartamento",
    transactionType: "venta",
    bedrooms: 3,
    bathrooms: 2,
    area: 180,
    yearBuilt: 2021,
    description: "Exclusivo apartamento en El Poblado con vista panorámica de la ciudad. Ubicado en una de las zonas más prestigiosas de Medellín, cuenta con excelentes vías de acceso, cerca del metro y rodeado de los mejores restaurantes y centros comerciales.",
    features: [
      "Vista panorámica de la ciudad",
      "Balcón amplio",
      "Acabados modernos",
      "Aire acondicionado",
      "Parqueadero privado",
      "Cuarto útil",
      "Piscina",
      "Zona BBQ"
    ],
    images: [
      "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "Ana López",
    agentPhone: "+57 316 682 7239",
    agentEmail: "ana@geniusindustries.org",
    createdAt: "2024-01-20T14:30:00Z",
    views: 156,
    isFavorite: true
  },
  {
    id: "3",
    title: "Oficina Corporativa en Alquiler - Santa Fe",
    price: 12000000,
    currency: "COP",
    location: "Santa Fe, Bogotá",
    address: "Avenida El Dorado #69-76, Santa Fe",
    propertyType: "Oficina",
    transactionType: "alquiler",
    bedrooms: 0,
    bathrooms: 4,
    area: 350,
    yearBuilt: 2018,
    description: "Moderna oficina corporativa en alquiler en el centro financiero de Bogotá. Ideal para empresas que buscan una imagen corporativa sólida en una ubicación estratégica con fácil acceso al aeropuerto y principales vías de la ciudad. Contrato mínimo 12 meses.",
    features: [
      "Pisos en porcelanato",
      "Divisiones en vidrio",
      "Sistema de aires centralizados",
      "Sala de juntas incluida",
      "Recepción equipada",
      "Cocina corporativa",
      "Estacionamiento para 8 vehículos",
      "Seguridad privada",
      "Internet fibra óptica",
      "Servicios incluidos"
    ],
    images: [
      "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1604328698692-f76ea9498e76?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "Roberto Silva",
    agentPhone: "+57 316 682 7239",
    agentEmail: "roberto@geniusindustries.org",
    createdAt: "2024-01-10T09:00:00Z",
    views: 89,
    isFavorite: false
  },
  {
    id: "4",
    title: "Casa Campestre en La Calera",
    price: 420000000,
    currency: "COP",
    location: "La Calera, Cundinamarca",
    address: "Vereda El Salitre, La Calera",
    propertyType: "Casa",
    transactionType: "venta",
    bedrooms: 5,
    bathrooms: 4,
    area: 450,
    yearBuilt: 2020,
    description: "Hermosa casa campestre con aire puro y tranquilidad, a solo 30 minutos de Bogotá. Perfecta para quienes buscan un escape de la ciudad sin alejarse demasiado. Cuenta con amplios jardines, zona de cultivo y vista a las montañas.",
    features: [
      "Jardín de 2000 m²",
      "Zona de cultivo orgánico",
      "Chimenea en sala principal",
      "Kiosco con BBQ",
      "Estudio independiente",
      "Garaje para 3 vehículos",
      "Pozo de agua",
      "Sistema de paneles solares"
    ],
    images: [
      "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "María González",
    agentPhone: "+57 316 682 7239",
    agentEmail: "maria@geniusindustries.org",
    createdAt: "2024-01-25T16:45:00Z",
    views: 312,
    isFavorite: false
  },
  {
    id: "5",
    title: "Local Comercial en Centro Histórico",
    price: 280000000,
    currency: "COP",
    location: "La Candelaria, Bogotá",
    address: "Carrera 7 #12-85, La Candelaria",
    propertyType: "Local Comercial",
    transactionType: "venta",
    bedrooms: 0,
    bathrooms: 2,
    area: 120,
    yearBuilt: 1950,
    description: "Local comercial en pleno centro histórico de Bogotá, ideal para restaurante, café o tienda especializada. Ubicación privilegiada con alto flujo peatonal y cerca de universidades y oficinas gubernamentales.",
    features: [
      "Fachada histórica restaurada",
      "Techos altos originales",
      "Vitrina amplia a la calle",
      "Bodega en segundo piso",
      "Instalaciones eléctricas nuevas",
      "Sistema de seguridad",
      "Cerca del transporte público",
      "Zona turística activa"
    ],
    images: [
      "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1590736969955-71cc94901144?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Vendido",
    agentName: "Jorge Ramírez",
    agentPhone: "+57 316 682 7239",
    agentEmail: "jorge@geniusindustries.org",
    createdAt: "2024-01-05T11:20:00Z",
    views: 445,
    isFavorite: false
  },
  {
    id: "6",
    title: "Penthouse en Zona T",
    price: 1850000000,
    currency: "COP",
    location: "Zona T, Bogotá",
    address: "Carrera 14 #82-84, Zona T",
    propertyType: "Apartamento",
    transactionType: "venta",
    bedrooms: 4,
    bathrooms: 5,
    area: 420,
    yearBuilt: 2022,
    description: "Espectacular penthouse de lujo en la exclusiva Zona T. Terraza privada de 200 m² con vista 360° de la ciudad, acabados premium y ubicación inmejorable en el corazón de la zona rosa bogotana.",
    features: [
      "Terraza privada 200 m²",
      "Vista 360° de la ciudad",
      "Jacuzzi en terraza",
      "Walk-in closet",
      "Cocina de isla premium",
      "Home theater",
      "Estudio privado",
      "Servicio de conserjería",
      "Ascensor privado",
      "3 parqueaderos"
    ],
    images: [
      "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1616137466211-f939a420be84?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1609688669309-fc15db557633?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "Patricia Vega",
    agentPhone: "+57 316 682 7239",
    agentEmail: "patricia@geniusindustries.org",
    createdAt: "2024-01-30T13:15:00Z",
    views: 67,
    isFavorite: true
  },
  {
    id: "7",
    title: "Apartamento en Alquiler - Chapinero",
    price: 2800000,
    currency: "COP",
    location: "Chapinero, Bogotá",
    address: "Carrera 11 #85-47, Chapinero",
    propertyType: "Apartamento",
    transactionType: "alquiler",
    bedrooms: 2,
    bathrooms: 2,
    area: 85,
    yearBuilt: 2019,
    description: "Moderno apartamento en alquiler en el corazón de Chapinero. Perfecto para profesionales o parejas. Ubicación estratégica con fácil acceso a TransMilenio, restaurantes, cafés y vida nocturna. Edificio con amenidades completas.",
    features: [
      "Balcón con vista a la ciudad",
      "Cocina americana equipada",
      "Aire acondicionado",
      "Closets empotrados",
      "Parqueadero privado",
      "Gimnasio en edificio",
      "Piscina",
      "Terraza social",
      "Seguridad 24/7",
      "Pet friendly"
    ],
    images: [
      "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "Laura Herrera",
    agentPhone: "+57 316 682 7239",
    agentEmail: "laura@geniusindustries.org",
    createdAt: "2024-02-01T08:30:00Z",
    views: 124,
    isFavorite: false
  },
  {
    id: "8",
    title: "Casa en Alquiler - Usaquén",
    price: 4500000,
    currency: "COP",
    location: "Usaquén, Bogotá",
    address: "Calle 116 #15-23, Usaquén",
    propertyType: "Casa",
    transactionType: "alquiler",
    bedrooms: 3,
    bathrooms: 3,
    area: 180,
    yearBuilt: 2020,
    description: "Hermosa casa en alquiler en Usaquén, zona exclusiva del norte de Bogotá. Ideal para familias que buscan tranquilidad sin alejarse de la ciudad. Cerca de colegios, centros comerciales y parques. Contrato mínimo 12 meses.",
    features: [
      "Jardín privado",
      "Chimenea",
      "Estudio independiente",
      "Cuarto de servicio",
      "Garaje para 2 carros",
      "Zona de lavandería",
      "Calentador solar",
      "Sistema de seguridad",
      "Cerca del Mercado de Pulgas",
      "Transporte público cercano"
    ],
    images: [
      "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80"
    ],
    status: "Disponible",
    agentName: "Diego Morales",
    agentPhone: "+57 316 682 7239",
    agentEmail: "diego@geniusindustries.org",
    createdAt: "2024-02-03T14:20:00Z",
    views: 89,
    isFavorite: false
  }
];

function MarketplacePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [properties, setProperties] = useState<Property[]>(sampleProperties);
  const [filteredProperties, setFilteredProperties] = useState<Property[]>(sampleProperties);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [filterType, setFilterType] = useState("all");
  const [filterTransaction, setFilterTransaction] = useState("all");
  const [priceRange, setPriceRange] = useState({ min: 0, max: 2000000000 });

  // Filtrar propiedades
  useEffect(() => {
    let filtered = properties.filter(property => {
      const matchesSearch = property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           property.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           property.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = filterType === "all" || property.propertyType.toLowerCase() === filterType.toLowerCase();
      
      const matchesTransaction = filterTransaction === "all" || property.transactionType === filterTransaction;
      
      const matchesPrice = property.price >= priceRange.min && property.price <= priceRange.max;
      
      return matchesSearch && matchesType && matchesTransaction && matchesPrice;
    });
    
    setFilteredProperties(filtered);
  }, [searchTerm, properties, filterType, filterTransaction, priceRange]);

  const formatPrice = (price: number, currency: string, transactionType: string) => {
    const formattedPrice = new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
    
    return transactionType === 'alquiler' ? `${formattedPrice}/mes` : formattedPrice;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const openPropertyModal = (property: Property) => {
    setSelectedProperty(property);
    setCurrentImageIndex(0);
    setShowModal(true);
    // Incrementar vistas (en el backend sería una llamada API)
    setProperties(prev => prev.map(p => 
      p.id === property.id ? { ...p, views: p.views + 1 } : p
    ));
  };

  const toggleFavorite = (propertyId: string) => {
    setProperties(prev => prev.map(p => 
      p.id === propertyId ? { ...p, isFavorite: !p.isFavorite } : p
    ));
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      "Disponible": "bg-green-600 text-white",
      "Vendido": "bg-red-600 text-white",
      "Reservado": "bg-yellow-600 text-white",
      "Alquilado": "bg-blue-600 text-white"
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusStyles[status as keyof typeof statusStyles] || 'bg-gray-600 text-white'}`}>
        {status}
      </span>
    );
  };

  const getTransactionBadge = (transactionType: string) => {
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
        transactionType === 'alquiler' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'
      }`}>
        {transactionType === 'alquiler' ? 'Alquiler' : 'Venta'}
      </span>
    );
  };

  return (
    <div className="bg-black min-h-screen py-16 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6">
            Encuentra tu Propiedad Ideal
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Descubre las mejores propiedades en Colombia con GENIUS INDUSTRIES. 
            Casas, apartamentos, oficinas y locales comerciales en las mejores ubicaciones.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-gray-900 rounded-2xl p-8 mb-12 border border-gray-700">
          <div className="grid lg:grid-cols-4 gap-6">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <FiSearch className="absolute left-3 top-3 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Buscar por ubicación, tipo o descripción..."
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:border-white focus:outline-none"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Property Type Filter */}
            <div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full py-3 px-4 bg-gray-800 text-white border border-gray-600 rounded-lg focus:border-white focus:outline-none"
              >
                <option value="all">Todos los tipos</option>
                <option value="casa">Casa</option>
                <option value="apartamento">Apartamento</option>
                <option value="oficina">Oficina</option>
                <option value="local comercial">Local Comercial</option>
              </select>
            </div>

            {/* Transaction Type Filter */}
            <div>
              <select
                value={filterTransaction}
                onChange={(e) => setFilterTransaction(e.target.value)}
                className="w-full py-3 px-4 bg-gray-800 text-white border border-gray-600 rounded-lg focus:border-white focus:outline-none"
              >
                <option value="all">Todos los tipos</option>
                <option value="venta">Venta</option>
                <option value="alquiler">Alquiler</option>
              </select>
            </div>

            {/* Quick Stats */}
            <div className="text-center">
              <div className="text-white">
                <div className="text-2xl font-bold">{filteredProperties.length}</div>
                <div className="text-gray-400 text-sm">Propiedades encontradas</div>
              </div>
            </div>
          </div>
        </div>

        {/* Properties Grid */}
        <div className="grid lg:grid-cols-3 md:grid-cols-2 gap-8 mb-12">
          {filteredProperties.map((property) => (
            <div key={property.id} className="bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border border-gray-700 hover:border-gray-600 transition-all duration-300 group">
              {/* Image */}
              <div className="relative">
                <img 
                  src={property.images[0]} 
                  alt={property.title} 
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-4 left-4">
                  {getStatusBadge(property.status)}
                </div>
                <div className="absolute top-4 right-4 flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(property.id);
                    }}
                    className={`p-2 rounded-full transition-all duration-200 ${
                      property.isFavorite ? 'bg-red-600 text-white' : 'bg-black bg-opacity-50 text-white hover:bg-red-600'
                    }`}
                  >
                    <FiHeart size={16} fill={property.isFavorite ? 'white' : 'none'} />
                  </button>
                  <div className="flex items-center gap-1 bg-black bg-opacity-50 text-white px-2 py-1 rounded-full text-xs">
                    <FiEye size={12} />
                    {property.views}
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-xl font-bold text-white group-hover:text-gray-300 transition-colors">
                    {property.title}
                  </h3>
                  <div className="text-white font-bold text-lg">
                    {formatPrice(property.price, property.currency, property.transactionType)}
                  </div>
                </div>

                <div className="flex items-center text-gray-400 mb-4">
                  <FiMapPin className="mr-2" size={16} />
                  <span className="text-sm">{property.location}</span>
                </div>

                <div className="flex items-center justify-between text-gray-300 text-sm mb-4">
                  {property.bedrooms > 0 && (
                    <div className="flex items-center gap-1">
                      <FaBed size={16} />
                      <span>{property.bedrooms}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <FaBath size={16} />
                    <span>{property.bathrooms}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <FiMaximize2 size={16} />
                    <span>{property.area} m²</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <FiCalendar size={16} />
                    <span>{property.yearBuilt}</span>
                  </div>
                </div>

                <p className="text-gray-400 text-sm leading-relaxed mb-4 line-clamp-2">
                  {property.description.length > 100 
                    ? `${property.description.substring(0, 100)}...` 
                    : property.description}
                </p>

                <div className="flex gap-3">
                  <button
                    onClick={() => openPropertyModal(property)}
                    className="flex-1 bg-white text-black font-semibold py-3 px-4 rounded-lg hover:bg-gray-200 transition-all duration-200"
                  >
                    Ver Detalles
                  </button>
                  <a
                    href={`https://wa.me/573166827239?text=Hola, estoy interesado en la propiedad: ${property.title} - ${formatPrice(property.price, property.currency, property.transactionType)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-3 border border-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-200 flex items-center justify-center"
                  >
                    <FiPhone size={18} />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* No Results */}
        {filteredProperties.length === 0 && (
          <div className="text-center py-16">
            <div className="text-gray-400 text-xl mb-4">No se encontraron propiedades</div>
            <p className="text-gray-500">Intenta ajustar tus filtros de búsqueda</p>
          </div>
        )}

        {/* Contact Section */}
        <div className="bg-gray-900 rounded-2xl p-12 text-center border border-gray-700">
          <h2 className="text-4xl font-bold text-white mb-6">¿No encuentras lo que buscas?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Contáctanos y te ayudamos a encontrar la propiedad perfecta para ti
          </p>
          <a
            href="https://wa.me/573166827239?text=Hola, necesito ayuda para encontrar una propiedad"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-white text-black font-semibold py-4 px-8 rounded-lg hover:bg-gray-200 transform hover:scale-105 transition-all duration-200 shadow-lg inline-flex items-center gap-2"
          >
            <FiPhone size={20} />
            Hablar con un Asesor
          </a>
        </div>
      </div>

      {/* Property Detail Modal */}
      {showModal && selectedProperty && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-700">
              <h2 className="text-2xl font-bold text-white">{selectedProperty.title}</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <FiX size={24} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {/* Image Gallery */}
              <div className="mb-6">
                <div className="relative mb-4">
                  <img
                    src={selectedProperty.images[currentImageIndex]}
                    alt={selectedProperty.title}
                    className="w-full h-96 object-cover rounded-lg"
                  />
                  <div className="absolute top-4 left-4">
                    {getStatusBadge(selectedProperty.status)}
                  </div>
                  <div className="absolute top-4 right-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
                    {currentImageIndex + 1} de {selectedProperty.images.length}
                  </div>
                </div>
                
                {selectedProperty.images.length > 1 && (
                  <div className="flex gap-2 overflow-x-auto">
                    {selectedProperty.images.map((image, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 ${
                          index === currentImageIndex ? 'border-white' : 'border-transparent'
                        }`}
                      >
                        <img
                          src={image}
                          alt={`Vista ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="grid lg:grid-cols-2 gap-8">
                {/* Property Info */}
                <div>
                  <div className="mb-6">
                    <div className="text-3xl font-bold text-white mb-2">
                      {formatPrice(selectedProperty.price, selectedProperty.currency, selectedProperty.transactionType)}
                    </div>
                    <div className="flex items-center text-gray-300 mb-4">
                      <FiMapPin className="mr-2" size={16} />
                      <span>{selectedProperty.address}</span>
                    </div>
                    <div className="text-gray-400 text-sm mb-4">
                      Publicado el {formatDate(selectedProperty.createdAt)} • {selectedProperty.views} vistas
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-gray-400 text-sm">Tipo</div>
                      <div className="text-white font-semibold">{selectedProperty.propertyType}</div>
                    </div>
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-gray-400 text-sm">Área</div>
                      <div className="text-white font-semibold">{selectedProperty.area} m²</div>
                    </div>
                    {selectedProperty.bedrooms > 0 && (
                      <div className="bg-gray-800 p-4 rounded-lg">
                        <div className="text-gray-400 text-sm">Habitaciones</div>
                        <div className="text-white font-semibold">{selectedProperty.bedrooms}</div>
                      </div>
                    )}
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-gray-400 text-sm">Baños</div>
                      <div className="text-white font-semibold">{selectedProperty.bathrooms}</div>
                    </div>
                  </div>

                  <div className="mb-6">
                    <h3 className="text-xl font-bold text-white mb-4">Descripción</h3>
                    <p className="text-gray-300 leading-relaxed">{selectedProperty.description}</p>
                  </div>

                  <div className="mb-6">
                    <h3 className="text-xl font-bold text-white mb-4">Características</h3>
                    <div className="grid grid-cols-1 gap-2">
                      {selectedProperty.features.map((feature, index) => (
                        <div key={index} className="flex items-center text-gray-300">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Agent Info & Actions */}
                <div>
                  <div className="bg-gray-800 rounded-xl p-6 mb-6">
                    <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                      <FiUser size={20} />
                      Agente Inmobiliario
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <div className="text-gray-400 text-sm">Nombre</div>
                        <div className="text-white font-semibold">{selectedProperty.agentName}</div>
                      </div>
                      <div>
                        <div className="text-gray-400 text-sm">Teléfono</div>
                        <div className="text-white">{selectedProperty.agentPhone}</div>
                      </div>
                      <div>
                        <div className="text-gray-400 text-sm">Email</div>
                        <div className="text-white">{selectedProperty.agentEmail}</div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <a
                      href={`https://wa.me/573166827239?text=Hola ${selectedProperty.agentName}, estoy interesado en la propiedad: ${selectedProperty.title} - ${formatPrice(selectedProperty.price, selectedProperty.currency, selectedProperty.transactionType)}. Me gustaría agendar una visita.`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full bg-green-600 text-white font-semibold py-4 px-6 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center justify-center gap-2"
                    >
                      <FiPhone size={20} />
                      Contactar por WhatsApp
                    </a>
                    
                    <a
                      href={`mailto:${selectedProperty.agentEmail}?subject=Consulta sobre ${selectedProperty.title}&body=Hola ${selectedProperty.agentName}, estoy interesado en la propiedad ${selectedProperty.title} ubicada en ${selectedProperty.address}. Me gustaría recibir más información.`}
                      className="w-full bg-gray-700 text-white font-semibold py-4 px-6 rounded-lg hover:bg-gray-600 transition-all duration-200 flex items-center justify-center gap-2"
                    >
                      <FiMail size={20} />
                      Enviar Email
                    </a>

                    <button
                      onClick={() => toggleFavorite(selectedProperty.id)}
                      className={`w-full font-semibold py-4 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 ${
                        selectedProperty.isFavorite 
                          ? 'bg-red-600 text-white hover:bg-red-700' 
                          : 'border border-gray-600 text-white hover:bg-gray-700'
                      }`}
                    >
                      <FiHeart size={20} fill={selectedProperty.isFavorite ? 'white' : 'none'} />
                      {selectedProperty.isFavorite ? 'Quitar de Favoritos' : 'Agregar a Favoritos'}
                    </button>

                    <div className="bg-gray-800 rounded-lg p-4">
                      <div className="text-center">
                        <div className="text-gray-400 text-sm mb-1">Construido en</div>
                        <div className="text-white font-bold text-lg">{selectedProperty.yearBuilt}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export const Route = createFileRoute("/marketplace")({
  component: MarketplacePage,
});
