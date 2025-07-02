import React, { useState, useEffect } from "react";
import { createFileRoute } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';
import { FiSearch, FiHome, FiTrendingUp, FiUsers, FiBriefcase, FiChevronLeft, FiChevronRight, FiStar, FiMapPin, FiCalendar, FiArrowRight, FiX, FiPhone, FiMail, FiClock, FiCheckCircle, FiUser, FiLogIn, FiUserPlus } from "react-icons/fi";
import { useUser, useAuth } from '@clerk/clerk-react';

// Función para obtener la URL de redirección basada en el rol
function getRedirectUrlByRole(role?: string): string {
  switch (role) {
    case 'CEO':
    case 'MANAGER':
    case 'SUPERVISOR':
    case 'HR':
    case 'AGENT':
    case 'SUPPORT':
      return '/admin'
    case 'CLIENT':
      return '/client-dashboard'
    default:
      return '/client-dashboard'
  }
}

// Interfaces TypeScript
interface Property {
  id: number;
  img: string;
  title: string;
  price: string;
  location: string;
  desc: string;
  type: string;
}

const featuredProperties: Property[] = [
  {
    id: 1,
    img: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80",
    title: "Casa Moderna en Bogotá",
    price: "$350,000 USD",
    location: "Bogotá, Colombia",
    desc: "4 habitaciones · 3 baños · 250m²",
    type: "Casa",
  },
  {
    id: 2,
    img: "https://images.unsplash.com/photo-1460518451285-97b6aa326961?auto=format&fit=crop&w=600&q=80",
    title: "Penthouse de Lujo",
    price: "$1,200,000 USD",
    location: "Medellín, Colombia",
    desc: "5 habitaciones · 5 baños · 500m²",
    type: "Penthouse",
  },
  {
    id: 3,
    img: "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=600&q=80",
    title: "Apartamento Ejecutivo",
    price: "$220,000 USD",
    location: "Cali, Colombia",
    desc: "2 habitaciones · 2 baños · 120m²",
    type: "Apartamento",
  },
];

const services = [
  { 
    icon: <FiHome className="text-white" size={36} />, 
    title: "Marketplace Inmobiliario", 
    desc: "Compra, vende o arrienda propiedades en las principales ciudades de Latinoamérica.",
    highlight: "25,000+ propiedades",
    link: "/marketplace"
  },
  { 
    icon: <FiTrendingUp className="text-white" size={36} />, 
    title: "Gestión de Activos", 
    desc: "Administración profesional de portafolios inmobiliarios y financieros con tecnología avanzada.",
    highlight: "ROI promedio 18%",
    link: "/investment"
  },
  { 
    icon: <FiBriefcase className="text-white" size={36} />, 
    title: "Inversiones Seguras", 
    desc: "Oportunidades de inversión verificadas con altos retornos y gestión de riesgo profesional.",
    highlight: "Riesgo controlado",
    link: "/investment"
  },
  { 
    icon: <FiUsers className="text-white" size={36} />, 
    title: "Asesoría Personalizada", 
    desc: "Expertos certificados que te acompañan en cada paso del proceso de inversión.",
    highlight: "Soporte 24/7",
    link: "/contact"
  },
];

const testimonials = [
  { 
    name: "Juan Pérez", 
    text: "GENIUS me ayudó a encontrar la casa de mis sueños en el mejor sector de Bogotá. El proceso fue transparente y profesional.", 
    rating: 5,
    role: "Inversionista",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=100&q=80"
  },
  { 
    name: "María López", 
    text: "Mi portafolio inmobiliario ha crecido 180% en 2 años. La gestión de activos de GENIUS es excepcional.", 
    rating: 5,
    role: "CEO Empresarial",
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?auto=format&fit=crop&w=100&q=80"
  },
  { 
    name: "Carlos Ruiz", 
    text: "La asesoría personalizada marcó la diferencia. Ahora tengo un portafolio diversificado que genera ingresos pasivos.", 
    rating: 5,
    role: "Arquitecto",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=100&q=80"
  },
];

function HomePage() {
  const [propertyIndex, setPropertyIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const { user, isLoaded } = useUser();
  const { signOut } = useAuth();
  
  // Modal states
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showVisitModal, setShowVisitModal] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  
  // Visit form states
  const [visitStep, setVisitStep] = useState(1);
  const [visitForm, setVisitForm] = useState({
    name: '',
    phone: '',
    date: '',
    time: ''
  });

  const getDashboardUrl = () => {
    if (!user) return '/client-dashboard';
    const userRole = user.publicMetadata?.role as string;
    return getRedirectUrlByRole(userRole);
  };

  const getUserDisplayName = () => {
    if (!user) return '';
    return user.firstName || user.emailAddresses[0]?.emailAddress || 'Usuario';
  };
  
  const nextProperty = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setPropertyIndex((i) => (i + 1) % featuredProperties.length);
    setTimeout(() => setIsAnimating(false), 500);
  };
  
  const prevProperty = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setPropertyIndex((i) => (i - 1 + featuredProperties.length) % featuredProperties.length);
    setTimeout(() => setIsAnimating(false), 500);
  };

  // Auto-advance carousel
  useEffect(() => {
    const timer = setInterval(() => {
      nextProperty();
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Modal handlers
  const openDetailsModal = (property: Property) => {
    setSelectedProperty(property);
    setShowDetailsModal(true);
  };

  const openVisitModal = (property: Property) => {
    setSelectedProperty(property);
    setShowVisitModal(true);
    setVisitStep(1);
    setVisitForm({ name: '', phone: '', date: '', time: '' });
  };

  const closeModals = () => {
    setShowDetailsModal(false);
    setShowVisitModal(false);
    setSelectedProperty(null);
  };

  const nextVisitStep = () => {
    if (visitStep < 4) setVisitStep(visitStep + 1);
  };

  const prevVisitStep = () => {
    if (visitStep > 1) setVisitStep(visitStep - 1);
  };

  const timeSlots = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"];

  const getPropertyDetails = (property: Property) => {
    const agentInfo = property.id === 1 
      ? { name: "María Rodríguez", phone: "+57 316 682 7239", email: "maria.rodriguez@geniusindustries.org" }
      : property.id === 2 
      ? { name: "Carlos Mendoza", phone: "+57 316 682 7240", email: "carlos.mendoza@geniusindustries.org" }
      : { name: "Ana Sofía López", phone: "+57 316 682 7241", email: "ana.lopez@geniusindustries.org" };
    
    const features = property.id === 1
      ? ["Piscina privada", "Jardín amplio", "Terraza panorámica", "Aire acondicionado", "Cocina integral", "Closets empotrados"]
      : property.id === 2
      ? ["Vista panorámica 360°", "Jacuzzi privado", "Terraza de 150m²", "Gimnasio privado", "Bodega de vinos", "Cuarto de servicio"]
      : ["Balcón con vista", "Zona BBQ comunal", "Gimnasio del edificio", "Piscina", "Portería 24 horas", "2 Ascensores"];
    
    return {
      ...property,
      agent: agentInfo,
      features,
      year: property.id === 1 ? '2019' : property.id === 2 ? '2021' : '2020',
      parking: property.id === 1 ? '2' : property.id === 2 ? '3' : '1',
      status: 'Disponible inmediato'
    };
  };

  return (
    <div className="w-full overflow-hidden">
      {/* Hero + Buscador - Mejorado */}
      <section className="relative bg-gradient-to-br from-black via-gray-900 to-black text-white py-32 px-4 flex flex-col items-center justify-center min-h-screen">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent transform rotate-12 scale-150"></div>
        </div>
        
        <div className="relative z-10 text-center max-w-6xl mx-auto">
          {/* Animated badge */}
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-6 py-2 mb-8 animate-pulse">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-ping"></div>
            <span className="text-sm font-medium text-white">Líderes en el mercado inmobiliario</span>
          </div>

          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black mb-6 text-center bg-gradient-to-r from-white via-gray-200 to-white bg-clip-text text-transparent leading-tight">
            Soluciones<br />
            <span className="bg-gradient-to-r from-gray-300 to-white bg-clip-text text-transparent">
              Inmobiliarias
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-12 text-center max-w-3xl mx-auto leading-relaxed">
            Liderando el mercado de bienes raíces e inversiones en Latinoamérica. 
            <span className="text-white font-semibold"> Encuentra tu propiedad ideal</span> o gestiona tu portafolio con expertos certificados.
          </p>
          
          {/* Buscador mejorado */}
          <form className="flex flex-col lg:flex-row gap-4 w-full max-w-4xl mx-auto bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-2xl border border-white/20">
            <div className="flex-1 flex items-center bg-white/10 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
              <FiSearch className="text-gray-300 mr-3" size={24} />
              <input 
                type="text" 
                placeholder="Buscar por ciudad, zona o código de propiedad..." 
                className="bg-transparent outline-none text-white w-full text-lg placeholder-gray-400 font-medium" 
              />
            </div>
            <button 
              type="submit" 
              className="bg-white text-black hover:bg-gray-100 transition-all duration-300 font-bold rounded-xl px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center gap-2 justify-center"
            >
              <span>Buscar Propiedades</span>
              <FiArrowRight size={20} />
            </button>
          </form>

          {/* Auth CTAs - Dynamic based on user status */}
          {isLoaded && (
            <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center items-center">
              {user ? (
                // Usuario autenticado
                <div className="text-center">
                  <p className="text-gray-300 mb-4">
                    ¡Bienvenido de vuelta, <span className="text-white font-semibold">{getUserDisplayName()}</span>!
                  </p>
                  <Link
                    to={getDashboardUrl()}
                    className="inline-flex items-center gap-3 bg-gradient-to-r from-white to-gray-100 text-black hover:from-gray-100 hover:to-white transition-all duration-300 font-bold rounded-xl px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                  >
                    <FiUser size={20} />
                    <span>Ir a mi Dashboard</span>
                    <FiArrowRight size={20} />
                  </Link>
                </div>
              ) : (
                // Usuario no autenticado
                <div className="text-center">
                  <p className="text-gray-300 mb-4">
                    ¿Listo para transformar tu patrimonio?
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <Link
                      to="/sign-up"
                      className="inline-flex items-center gap-3 bg-gradient-to-r from-white to-gray-100 text-black hover:from-gray-100 hover:to-white transition-all duration-300 font-bold rounded-xl px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                    >
                      <FiUserPlus size={20} />
                      <span>Registrarme como Cliente</span>
                      <FiArrowRight size={20} />
                    </Link>
                    <Link
                      to="/sign-in"
                      className="inline-flex items-center gap-3 border-2 border-white text-white hover:bg-white hover:text-black transition-all duration-300 font-bold rounded-xl px-8 py-4"
                    >
                      <FiLogIn size={20} />
                      <span>Iniciar Sesión</span>
                    </Link>
                  </div>
                  <p className="text-xs text-gray-400 mt-3">
                    * El registro está disponible únicamente para clientes.<br />
                    Los usuarios corporativos son creados por el administrador.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-black text-white mb-2">25,000+</div>
              <div className="text-gray-400">Propiedades Activas</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-white mb-2">$2.5B+</div>
              <div className="text-gray-400">Valor en Transacciones</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-white mb-2">15,000+</div>
              <div className="text-gray-400">Clientes Satisfechos</div>
            </div>
          </div>
        </div>
      </section>

      {/* Carousel de propiedades - Completamente rediseñado */}
      <section className="py-24 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
              Propiedades <span className="text-gray-400">Destacadas</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Descubre las mejores oportunidades de inversión en propiedades premium seleccionadas por nuestros expertos
            </p>
          </div>

          <div className="relative">
            {/* Property card */}
            <div className="flex justify-center">
              <div className={`bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl overflow-hidden shadow-2xl border border-gray-700 max-w-4xl w-full transform transition-all duration-500 ${isAnimating ? 'scale-95 opacity-75' : 'scale-100 opacity-100'}`}>
                <div className="flex flex-col lg:flex-row">
                  {/* Image */}
                  <div className="lg:w-1/2 relative overflow-hidden">
                    <img 
                      src={featuredProperties[propertyIndex].img} 
                      alt="Propiedad" 
                      className="w-full h-80 lg:h-96 object-cover transform hover:scale-110 transition-transform duration-700" 
                    />
                    <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm font-semibold">
                      {featuredProperties[propertyIndex].type}
                    </div>
                    <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm text-black px-3 py-1 rounded-full text-sm font-bold">
                      Disponible
                    </div>
                  </div>
                  
                  {/* Content */}
                  <div className="lg:w-1/2 p-8 lg:p-12 flex flex-col justify-center">
                    <h3 className="text-3xl lg:text-4xl font-black text-white mb-4">
                      {featuredProperties[propertyIndex].title}
                    </h3>
                    
                    <div className="text-2xl lg:text-3xl font-black text-white mb-6">
                      {featuredProperties[propertyIndex].price}
                    </div>
                    
                    <div className="flex items-center gap-2 text-gray-300 mb-2">
                      <FiMapPin size={18} />
                      <span className="text-lg">{featuredProperties[propertyIndex].location}</span>
                    </div>
                    
                    <div className="text-gray-400 mb-8 text-lg">
                      {featuredProperties[propertyIndex].desc}
                    </div>
                    
                    <div className="flex gap-4">
                      <button 
                        onClick={() => openDetailsModal(featuredProperties[propertyIndex])}
                        className="bg-white text-black hover:bg-gray-100 transition-all duration-300 px-8 py-4 rounded-xl font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center gap-2"
                      >
                        <span>Ver Detalles</span>
                        <FiArrowRight size={20} />
                      </button>
                      <button 
                        onClick={() => openVisitModal(featuredProperties[propertyIndex])}
                        className="border-2 border-white text-white hover:bg-white hover:text-black transition-all duration-300 px-8 py-4 rounded-xl font-bold flex items-center gap-2"
                      >
                        <FiCalendar size={20} />
                        <span>Agendar Visita</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation buttons */}
            <button 
              onClick={prevProperty} 
              disabled={isAnimating}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/10 backdrop-blur-sm hover:bg-white/20 disabled:opacity-50 rounded-full p-4 shadow-lg transition-all duration-300 border border-white/20"
            >
              <FiChevronLeft size={32} className="text-white" />
            </button>
            
            <button 
              onClick={nextProperty} 
              disabled={isAnimating}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/10 backdrop-blur-sm hover:bg-white/20 disabled:opacity-50 rounded-full p-4 shadow-lg transition-all duration-300 border border-white/20"
            >
              <FiChevronRight size={32} className="text-white" />
            </button>
          </div>

          {/* Indicators */}
          <div className="flex justify-center gap-3 mt-12">
            {featuredProperties.map((_, index) => (
              <button
                key={index}
                onClick={() => setPropertyIndex(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === propertyIndex 
                    ? 'bg-white scale-125' 
                    : 'bg-white/30 hover:bg-white/50'
                }`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Servicios - Completamente rediseñados */}
      <section className="py-24 bg-black relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0">
          <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-gray-900/20 to-transparent"></div>
          <div className="absolute bottom-0 left-0 w-1/3 h-full bg-gradient-to-r from-gray-900/20 to-transparent"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
              Nuestros <span className="text-gray-400">Servicios</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Soluciones integrales para maximizar tu patrimonio inmobiliario con la confianza de más de 15,000 clientes satisfechos
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {services.map((service, index) => (
              <div 
                key={service.title} 
                onClick={() => {
                  const links = ["/marketplace", "/investment", "/investment", "/contact"];
                  window.location.href = links[index];
                }}
                className="group bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl p-8 shadow-2xl border border-gray-700 hover:border-gray-500 transition-all duration-500 transform hover:-translate-y-2 hover:scale-105 relative overflow-hidden cursor-pointer"
              >
                {/* Background effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                
                {/* Content */}
                <div className="relative z-10">
                  {/* Icon container */}
                  <div className="w-20 h-20 bg-gradient-to-br from-white/10 to-white/5 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    {service.icon}
                  </div>
                  
                  {/* Highlight badge */}
                  <div className="inline-block bg-white/10 backdrop-blur-sm text-white text-xs font-bold px-3 py-1 rounded-full mb-4">
                    {service.highlight}
                  </div>
                  
                  <h3 className="font-black text-xl text-white mb-4 group-hover:text-gray-100 transition-colors">
                    {service.title}
                  </h3>
                  
                  <p className="text-gray-400 leading-relaxed mb-6 group-hover:text-gray-300 transition-colors">
                    {service.desc}
                  </p>
                  
                  {/* CTA */}
                  <div className="flex items-center text-white font-semibold opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                    <span className="mr-2">Conocer más</span>
                    <FiArrowRight size={16} />
                  </div>
                </div>

                {/* Number indicator */}
                <div className="absolute top-6 right-6 text-6xl font-black text-white/5 group-hover:text-white/10 transition-colors duration-300">
                  {String(index + 1).padStart(2, '0')}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonios - Completamente rediseñados */}
      <section className="py-24 bg-gradient-to-b from-black to-gray-900 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-white rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
              Lo que dicen <span className="text-gray-400">nuestros clientes</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Historias reales de éxito de inversionistas que han transformado su patrimonio con GENIUS INDUSTRIES
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div 
                key={testimonial.name} 
                className="group bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl p-8 shadow-2xl border border-gray-700 hover:border-gray-500 transition-all duration-500 transform hover:-translate-y-2 relative overflow-hidden"
              >
                {/* Background effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                
                {/* Content */}
                <div className="relative z-10">
                  {/* Stars */}
                  <div className="flex gap-1 mb-6">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <FiStar key={i} className="text-yellow-400 fill-current" size={20} />
                    ))}
                  </div>
                  
                  {/* Quote */}
                  <blockquote className="text-gray-300 text-lg leading-relaxed mb-8 italic group-hover:text-gray-200 transition-colors">
                    "{testimonial.text}"
                  </blockquote>
                  
                  {/* Author */}
                  <div className="flex items-center gap-4">
                    <img 
                      src={testimonial.avatar} 
                      alt={testimonial.name}
                      className="w-16 h-16 rounded-full object-cover border-2 border-gray-600 group-hover:border-gray-400 transition-colors"
                    />
                    <div>
                      <div className="text-white font-bold text-lg">{testimonial.name}</div>
                      <div className="text-gray-400 text-sm">{testimonial.role}</div>
                    </div>
                  </div>
                </div>

                {/* Quote mark decoration */}
                <div className="absolute top-6 right-6 text-6xl font-black text-white/5 group-hover:text-white/10 transition-colors duration-300">
                  "
                </div>
              </div>
            ))}
          </div>

          {/* Final CTA - Dynamic */}
          {isLoaded && (
            <div className="text-center mt-16">
              {user ? (
                <>
                  <p className="text-gray-400 mb-8 text-lg">
                    ¿Listo para expandir tu portafolio inmobiliario?
                  </p>
                  <Link
                    to={getDashboardUrl()}
                    className="bg-white text-black hover:bg-gray-100 transition-all duration-300 font-bold px-10 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 inline-flex items-center gap-3"
                  >
                    <FiUser size={20} />
                    <span>Explorar mi Dashboard</span>
                    <FiArrowRight size={20} />
                  </Link>
                </>
              ) : (
                <>
                  <p className="text-gray-400 mb-8 text-lg">¿Quieres ser el próximo caso de éxito?</p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                      to="/sign-up"
                      className="bg-white text-black hover:bg-gray-100 transition-all duration-300 font-bold px-10 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 inline-flex items-center gap-3"
                    >
                      <FiUserPlus size={20} />
                      <span>Comenzar mi inversión</span>
                      <FiArrowRight size={20} />
                    </Link>
                    <Link
                      to="/sign-in"
                      className="border-2 border-white text-white hover:bg-white hover:text-black transition-all duration-300 font-bold px-10 py-4 rounded-xl inline-flex items-center gap-3"
                    >
                      <FiLogIn size={20} />
                      <span>Ya tengo cuenta</span>
                    </Link>
                  </div>
                  <p className="text-xs text-gray-500 mt-4">
                    Solo se permite registro directo para clientes. Los usuarios corporativos son gestionados por el CEO.
                  </p>
                </>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Modal de Detalles de Propiedad */}
      {showDetailsModal && selectedProperty && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700 shadow-2xl">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-700">
              <h2 className="text-3xl font-black text-white">Detalles de la Propiedad</h2>
              <button 
                onClick={closeModals}
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
              >
                <FiX size={24} />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {(() => {
                const details = getPropertyDetails(selectedProperty);
                return (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Image */}
                    <div className="relative">
                      <img 
                        src={selectedProperty.img} 
                        alt={selectedProperty.title}
                        className="w-full h-80 object-cover rounded-2xl"
                      />
                      <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm font-semibold">
                        {selectedProperty.type}
                      </div>
                    </div>

                    {/* Details */}
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-2xl font-black text-white mb-2">{selectedProperty.title}</h3>
                        <div className="text-3xl font-black text-white mb-4">{selectedProperty.price}</div>
                        <div className="flex items-center gap-2 text-gray-300 mb-4">
                          <FiMapPin size={18} />
                          <span>{selectedProperty.location}</span>
                        </div>
                        <p className="text-gray-400 text-lg">{selectedProperty.desc}</p>
                      </div>

                      {/* Characteristics */}
                      <div>
                        <h4 className="text-xl font-bold text-white mb-3">Características Premium</h4>
                        <div className="grid grid-cols-1 gap-2">
                          {details.features.map((feature, index) => (
                            <div key={index} className="flex items-center gap-2 text-gray-300">
                              <div className="w-2 h-2 bg-white rounded-full"></div>
                              <span>{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Additional Info */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-black/30 rounded-xl p-4">
                          <div className="text-gray-400 text-sm">Año construcción</div>
                          <div className="text-white font-bold">{details.year}</div>
                        </div>
                        <div className="bg-black/30 rounded-xl p-4">
                          <div className="text-gray-400 text-sm">Parqueaderos</div>
                          <div className="text-white font-bold">{details.parking}</div>
                        </div>
                      </div>

                      {/* Agent Info */}
                      <div className="bg-gradient-to-r from-black/40 to-gray-800/40 rounded-2xl p-6">
                        <h4 className="text-xl font-bold text-white mb-4">Agente Especializado</h4>
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <FiUser className="text-gray-400" size={20} />
                            <span className="text-white font-semibold">{details.agent.name}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <FiPhone className="text-gray-400" size={20} />
                            <span className="text-gray-300">{details.agent.phone}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <FiMail className="text-gray-400" size={20} />
                            <span className="text-gray-300">{details.agent.email}</span>
                          </div>
                        </div>
                      </div>

                      {/* Status */}
                      <div className="flex items-center gap-2 text-green-400">
                        <FiCheckCircle size={20} />
                        <span className="font-semibold">{details.status}</span>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Action buttons */}
              <div className="flex gap-4 mt-8 pt-6 border-t border-gray-700">
                <button 
                  onClick={() => {
                    closeModals();
                    openVisitModal(selectedProperty);
                  }}
                  className="flex-1 bg-white text-black hover:bg-gray-100 transition-all duration-300 px-8 py-4 rounded-xl font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center gap-2 justify-center"
                >
                  <FiCalendar size={20} />
                  <span>Agendar Visita</span>
                </button>
                <button 
                  onClick={closeModals}
                  className="px-8 py-4 border-2 border-gray-600 text-gray-300 hover:text-white hover:border-gray-400 transition-all duration-300 rounded-xl font-bold"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Agendar Visita */}
      {showVisitModal && selectedProperty && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl max-w-2xl w-full border border-gray-700 shadow-2xl">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-700">
              <div>
                <h2 className="text-3xl font-black text-white">Agendar Visita</h2>
                <p className="text-gray-400 mt-1">{selectedProperty.title}</p>
              </div>
              <button 
                onClick={closeModals}
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
              >
                <FiX size={24} />
              </button>
            </div>

            {/* Progress Steps */}
            <div className="px-6 py-4 border-b border-gray-700">
              <div className="flex items-center justify-between">
                {[1, 2, 3, 4].map((step) => (
                  <div key={step} className="flex items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                      visitStep >= step ? 'bg-white text-black' : 'bg-gray-700 text-gray-400'
                    }`}>
                      {visitStep > step ? <FiCheckCircle /> : step}
                    </div>
                    {step < 4 && (
                      <div className={`w-12 h-1 mx-2 ${visitStep > step ? 'bg-white' : 'bg-gray-700'}`}></div>
                    )}
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-sm text-gray-400 mt-2">
                <span>Información</span>
                <span>Contacto</span>
                <span>Fecha</span>
                <span>Confirmación</span>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 min-h-[300px]">
              {visitStep === 1 && (
                <div className="space-y-6">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-4">¡Hola! 👋</h3>
                    <p className="text-gray-300 text-lg">
                      Soy {getPropertyDetails(selectedProperty).agent.name}, tu agente especializado.
                      Te ayudaré con la visita a esta increíble propiedad.
                    </p>
                  </div>
                  <div className="bg-black/30 rounded-2xl p-6">
                    <h4 className="text-lg font-bold text-white mb-2">¿Cuál es tu nombre completo?</h4>
                    <input
                      type="text"
                      value={visitForm.name}
                      onChange={(e) => setVisitForm({...visitForm, name: e.target.value})}
                      placeholder="Ingresa tu nombre completo"
                      className="w-full bg-white/10 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-white transition-colors"
                    />
                  </div>
                </div>
              )}

              {visitStep === 2 && (
                <div className="space-y-6">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-4">Perfecto {visitForm.name}! 📱</h3>
                    <p className="text-gray-300 text-lg">
                      ¿Cuál es tu número de teléfono? Lo necesito para coordinar la visita y enviarte todos los detalles.
                    </p>
                  </div>
                  <div className="bg-black/30 rounded-2xl p-6">
                    <h4 className="text-lg font-bold text-white mb-2">Número de teléfono</h4>
                    <input
                      type="tel"
                      value={visitForm.phone}
                      onChange={(e) => setVisitForm({...visitForm, phone: e.target.value})}
                      placeholder="+57 XXX XXX XXXX"
                      className="w-full bg-white/10 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-white transition-colors"
                    />
                  </div>
                </div>
              )}

              {visitStep === 3 && (
                <div className="space-y-6">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-white mb-4">¡Excelente! 📅</h3>
                    <p className="text-gray-300 text-lg">
                      ¿Qué día te gustaría visitarla? Selecciona la fecha y hora que mejor te convenga.
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-black/30 rounded-2xl p-6">
                      <h4 className="text-lg font-bold text-white mb-2">Fecha</h4>
                      <input
                        type="date"
                        value={visitForm.date}
                        onChange={(e) => setVisitForm({...visitForm, date: e.target.value})}
                        min={new Date().toISOString().split('T')[0]}
                        className="w-full bg-white/10 border border-gray-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white transition-colors"
                      />
                    </div>
                    <div className="bg-black/30 rounded-2xl p-6">
                      <h4 className="text-lg font-bold text-white mb-2">Horario</h4>
                      <select
                        value={visitForm.time}
                        onChange={(e) => setVisitForm({...visitForm, time: e.target.value})}
                        className="w-full bg-white/10 border border-gray-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white transition-colors"
                      >
                        <option value="">Selecciona un horario</option>
                        {timeSlots.map((time) => (
                          <option key={time} value={time} className="bg-gray-800">{time}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {visitStep === 4 && (
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="text-6xl mb-4">🎉</div>
                    <h3 className="text-2xl font-bold text-white mb-4">¡CITA CONFIRMADA!</h3>
                  </div>
                  <div className="bg-gradient-to-r from-green-900/40 to-green-800/40 rounded-2xl p-6 border border-green-700">
                    <div className="space-y-3 text-white">
                      <div><strong>Cliente:</strong> {visitForm.name}</div>
                      <div><strong>Teléfono:</strong> {visitForm.phone}</div>
                      <div><strong>Propiedad:</strong> {selectedProperty.title}</div>
                      <div><strong>Ubicación:</strong> {selectedProperty.location}</div>
                      <div><strong>Fecha:</strong> {visitForm.date}</div>
                      <div><strong>Hora:</strong> {visitForm.time}</div>
                      <div><strong>Agente:</strong> {getPropertyDetails(selectedProperty).agent.name}</div>
                    </div>
                  </div>
                  <div className="bg-black/30 rounded-2xl p-6">
                    <h4 className="text-lg font-bold text-white mb-3">Detalles de la visita:</h4>
                    <ul className="text-gray-300 space-y-2">
                      <li>• Te contactaré 1 día antes para confirmar</li>
                      <li>• La visita dura aproximadamente 45 minutos</li>
                      <li>• Puedes traer acompañantes</li>
                      <li>• Tendremos toda la documentación disponible</li>
                    </ul>
                    <div className="mt-4 pt-4 border-t border-gray-700 text-center">
                      <div className="text-white font-bold text-lg">GENIUS INDUSTRIES</div>
                      <div className="text-gray-400 italic">"Tu patrimonio, nuestra pasión"</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex gap-4 p-6 border-t border-gray-700">
              {visitStep > 1 && visitStep < 4 && (
                <button 
                  onClick={prevVisitStep}
                  className="px-6 py-3 border-2 border-gray-600 text-gray-300 hover:text-white hover:border-gray-400 transition-all duration-300 rounded-xl font-bold"
                >
                  Anterior
                </button>
              )}
              
              {visitStep < 4 ? (
                <button 
                  onClick={nextVisitStep}
                  disabled={
                    (visitStep === 1 && !visitForm.name) ||
                    (visitStep === 2 && !visitForm.phone) ||
                    (visitStep === 3 && (!visitForm.date || !visitForm.time))
                  }
                  className="flex-1 bg-white text-black hover:bg-gray-100 disabled:bg-gray-600 disabled:text-gray-400 transition-all duration-300 px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-1 disabled:transform-none disabled:hover:shadow-none"
                >
                  {visitStep === 3 ? 'Confirmar Cita' : 'Siguiente'}
                </button>
              ) : (
                <button 
                  onClick={closeModals}
                  className="flex-1 bg-white text-black hover:bg-gray-100 transition-all duration-300 px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  ¡Perfecto!
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export const Route = createFileRoute('/')({
  component: HomePage,
}); 