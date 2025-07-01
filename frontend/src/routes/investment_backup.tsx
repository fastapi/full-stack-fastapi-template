import React, { useState } from "react";
import { createFileRoute } from '@tanstack/react-router';
import { FiTrendingUp, FiShield, FiDollarSign, FiBarChart2, FiTarget, FiAward, FiBriefcase, FiGlobe, FiActivity, FiHome, FiArrowUpRight } from "react-icons/fi";

const investmentServices = [
  { 
    icon: <FiHome className="text-white" size={32} />, 
    title: "Inversiones Inmobiliarias", 
    desc: "Proyectos residenciales, comerciales e industriales con alta rentabilidad y seguridad jurídica.",
    roi: "15-25%",
    risk: "Bajo",
    category: "real-estate"
  },
  { 
    icon: <FiTrendingUp className="text-white" size={32} />, 
    title: "Fondos de Inversión en Acciones", 
    desc: "Diversificación en mercados internacionales con gestión profesional y estrategias probadas.",
    roi: "8-18%",
    risk: "Medio",
    category: "stocks"
  },
  { 
    icon: <FiActivity className="text-white" size={32} />, 
    title: "Trading de Criptomonedas", 
    desc: "Fondos especializados en criptoactivos con estrategias algorítmicas y gestión activa.",
    roi: "20-50%",
    risk: "Alto",
    category: "crypto"
  },
  { 
    icon: <FiBarChart2 className="text-white" size={32} />, 
    title: "Trading Tradicional", 
    desc: "Operaciones en Forex, commodities y derivados con tecnología de vanguardia.",
    roi: "12-30%",
    risk: "Medio-Alto",
    category: "trading"
  },
];

const detailedOpportunities = [
  {
    title: "Torres Residenciales Premium",
    category: "Inmobiliario",
    roi: "22%",
    minInvestment: "$50,000 USD",
    duration: "24 meses",
    status: "Disponible",
    image: "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80",
    highlights: ["Ubicación estratégica", "Entrega garantizada", "Plusvalía proyectada 35%"]
  },
  {
    title: "Fondo Global de Tecnología",
    category: "Acciones",
    roi: "15%",
    minInvestment: "$10,000 USD",
    duration: "12 meses",
    status: "Últimas plazas",
    image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=400&q=80",
    highlights: ["FAANG + Tesla", "Gestión profesional", "Diversificación global"]
  },
  {
    title: "Crypto DeFi Fund",
    category: "Criptomonedas",
    roi: "35%",
    minInvestment: "$5,000 USD",
    duration: "6 meses",
    status: "Alta demanda",
    image: "https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=400&q=80",
    highlights: ["Staking automático", "Yield farming", "Protocolos auditados"]
  },
  {
    title: "Forex Algoritmo Premium",
    category: "Trading",
    roi: "28%",
    minInvestment: "$25,000 USD", 
    duration: "18 meses",
    status: "Disponible",
    image: "https://images.unsplash.com/photo-1590736969955-71cc94901144?auto=format&fit=crop&w=400&q=80",
    highlights: ["IA avanzada", "Risk management", "Drawdown máximo 8%"]
  }
];

const benefits = [
  { 
    icon: <FiShield className="text-white" size={28} />, 
    title: "Seguridad Garantizada", 
    desc: "Regulación internacional y seguros de inversión"
  },
  { 
    icon: <FiDollarSign className="text-white" size={28} />, 
    title: "Liquidez Flexible", 
    desc: "Opciones de retiro anticipado en la mayoría de fondos"
  },
  { 
    icon: <FiBriefcase className="text-white" size={28} />, 
    title: "Gestión Profesional", 
    desc: "Equipo de expertos con más de 15 años de experiencia"
  },
  { 
    icon: <FiGlobe className="text-white" size={28} />, 
    title: "Diversificación Global", 
    desc: "Acceso a mercados internacionales y activos diversos"
  },
];

function InvestmentPage() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showOpportunities, setShowOpportunities] = useState(false);

  const whatsappNumber = "+573001234567"; // Número de WhatsApp de la entidad
  const whatsappMessage = "Hola, me interesa obtener asesoría sobre las oportunidades de inversión en GENIUS INDUSTRIES. ¿Podrían brindarme más información?";
  const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(whatsappMessage)}`;

  const filteredOpportunities = selectedCategory === 'all' 
    ? detailedOpportunities 
    : detailedOpportunities.filter(opp => {
        if (selectedCategory === 'real-estate') return opp.category === 'Inmobiliario';
        if (selectedCategory === 'stocks') return opp.category === 'Acciones';
        if (selectedCategory === 'crypto') return opp.category === 'Criptomonedas';
        if (selectedCategory === 'trading') return opp.category === 'Trading';
        return true;
      });

  const getRiskColor = (risk: string) => {
    switch(risk) {
      case 'Bajo': return 'bg-green-600';
      case 'Medio': return 'bg-yellow-600';
      case 'Medio-Alto': return 'bg-orange-600';
      case 'Alto': return 'bg-red-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <div className="bg-black min-h-screen py-16 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6">
            Inversiones Diversificadas
          </h1>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto mb-8">
            Maximiza tu capital con nuestro ecosistema completo de inversiones: inmobiliaria, acciones, 
            criptomonedas y trading profesional. Rentabilidad, seguridad y crecimiento sostenible.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button 
              onClick={() => setShowOpportunities(!showOpportunities)}
              className="bg-white text-black font-semibold py-4 px-8 rounded-lg hover:bg-gray-200 transform hover:scale-105 transition-all duration-200 shadow-lg flex items-center gap-2"
            >
              <FiTarget size={20} />
              Ver Oportunidades
            </button>
            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="border-2 border-white text-white font-semibold py-4 px-8 rounded-lg hover:bg-white hover:text-black transition-all duration-200 flex items-center gap-2"
            >
              <FiArrowUpRight size={20} />
              Solicitar Asesoría
            </a>
          </div>
        </div>

        {/* Investment Services */}
        <div className="mb-16">
          <h2 className="text-4xl font-bold text-white mb-12 text-center">Nuestros Servicios de Inversión</h2>
          <div className="grid lg:grid-cols-2 gap-8">
            {investmentServices.map((service, index) => (
              <div key={index} className="bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-700 hover:border-gray-600 transition-all duration-300 group">
                <div className="flex items-start justify-between mb-6">
                  <div className="p-4 bg-gray-700 rounded-xl group-hover:scale-110 transition-transform duration-300">
                    {service.icon}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white mb-1">{service.roi}</div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${getRiskColor(service.risk)}`}>
                      {service.risk}
                    </span>
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{service.title}</h3>
                <p className="text-gray-300 leading-relaxed mb-6">{service.desc}</p>
                <button 
                  onClick={() => setSelectedCategory(service.category)}
                  className="text-white hover:text-gray-300 font-medium flex items-center gap-2 transition-colors"
                >
                  Ver detalles <FiArrowUpRight size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Benefits */}
        <div className="grid md:grid-cols-4 gap-6 mb-16">
          {benefits.map((benefit, index) => (
            <div key={index} className="bg-gray-900 rounded-xl p-6 text-center border border-gray-700">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-gray-700 rounded-lg">
                  {benefit.icon}
                </div>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{benefit.title}</h3>
              <p className="text-gray-400 text-sm">{benefit.desc}</p>
            </div>
          ))}
        </div>

        {/* Detailed Opportunities Section */}
        {showOpportunities && (
          <div className="mb-16 animate-fadeIn">
            <div className="bg-gray-900 rounded-2xl p-8 border border-gray-700">
              <div className="text-center mb-8">
                <h2 className="text-4xl font-bold text-white mb-4 flex items-center justify-center gap-3">
                  <FiTarget className="text-white" />
                  Oportunidades Disponibles
                </h2>
                <p className="text-xl text-gray-300">Invierte en las mejores oportunidades del mercado</p>
              </div>

              {/* Filter Buttons */}
              <div className="flex flex-wrap justify-center gap-4 mb-8">
                {[
                  { key: 'all', label: 'Todas' },
                  { key: 'real-estate', label: 'Inmobiliario' },
                  { key: 'stocks', label: 'Acciones' },
                  { key: 'crypto', label: 'Crypto' },
                  { key: 'trading', label: 'Trading' }
                ].map(filter => (
                  <button
                    key={filter.key}
                    onClick={() => setSelectedCategory(filter.key)}
                    className={`px-6 py-3 rounded-lg font-medium transition-all ${
                      selectedCategory === filter.key
                        ? 'bg-white text-black'
                        : 'bg-gray-700 text-white hover:bg-gray-600'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>

              {/* Opportunities Grid */}
              <div className="grid lg:grid-cols-2 xl:grid-cols-2 gap-8">
                {filteredOpportunities.map((opportunity, index) => (
                  <div key={index} className="bg-gray-800 rounded-2xl overflow-hidden shadow-xl border border-gray-700 hover:border-gray-600 transition-all duration-300 group">
                    <div className="relative overflow-hidden">
                      <img 
                        src={opportunity.image} 
                        alt={opportunity.title}
                        className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300"
                      />
                      <div className="absolute top-4 right-4">
                        <span className="bg-white text-black px-3 py-1 rounded-full text-sm font-medium">
                          {opportunity.category}
                        </span>
                      </div>
                      <div className="absolute bottom-4 left-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium text-white ${
                          opportunity.status === 'Disponible' ? 'bg-green-600' :
                          opportunity.status === 'Últimas plazas' ? 'bg-yellow-600' :
                          opportunity.status === 'Alta demanda' ? 'bg-red-600' :
                          'bg-gray-600'
                        }`}>
                          {opportunity.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <h3 className="text-xl font-bold text-white mb-3">{opportunity.title}</h3>
                      
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        <div>
                          <p className="text-gray-400 text-sm">ROI Proyectado</p>
                          <p className="text-white font-bold text-lg">{opportunity.roi}</p>
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm">Inversión mínima</p>
                          <p className="text-white font-bold text-lg">{opportunity.minInvestment}</p>
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm">Duración</p>
                          <p className="text-white font-bold text-lg">{opportunity.duration}</p>
                        </div>
                      </div>

                      <div className="mb-6">
                        <p className="text-gray-400 text-sm mb-2">Puntos destacados:</p>
                        <ul className="space-y-1">
                          {opportunity.highlights.map((highlight, i) => (
                            <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
                              <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                              {highlight}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="flex gap-3">
                        <button className="flex-1 bg-white text-black font-semibold py-3 px-4 rounded-lg hover:bg-gray-200 transition-all duration-200">
                          Más información
                        </button>
                        <a
                          href={whatsappUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-3 border border-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-200 flex items-center justify-center"
                        >
                          <FiArrowUpRight size={18} />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Why Choose Us */}
        <div className="bg-gray-900 rounded-2xl p-12 text-center border border-gray-700">
          <div className="flex items-center justify-center gap-3 mb-6">
            <FiAward className="text-white text-3xl" />
            <h2 className="text-4xl font-bold text-white">¿Por qué GENIUS INDUSTRIES?</h2>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8 mt-12">
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">+500</div>
              <p className="text-gray-300">Proyectos exitosos</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">$50M+</div>
              <p className="text-gray-300">Capital gestionado</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">15 años</div>
              <p className="text-gray-300">De experiencia</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">98%</div>
              <p className="text-gray-300">Satisfacción del cliente</p>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white text-black font-semibold py-4 px-8 rounded-lg hover:bg-gray-200 transform hover:scale-105 transition-all duration-200 shadow-lg flex items-center gap-2"
            >
              <FiArrowUpRight size={20} />
              Comenzar mi inversión
            </a>
            <button 
              onClick={() => setShowOpportunities(true)}
              className="border-2 border-white text-white font-semibold py-4 px-8 rounded-lg hover:bg-white hover:text-black transition-all duration-200"
            >
              Explorar oportunidades
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute('/investment_backup')({
  component: InvestmentPage,
}); 
