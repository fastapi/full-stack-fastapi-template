import React, { useState } from "react";
import { createFileRoute } from '@tanstack/react-router';
import { FiTrendingUp, FiShield, FiDollarSign, FiBarChart2, FiTarget, FiAward, FiBriefcase, FiGlobe, FiActivity, FiHome, FiArrowUpRight, FiClock, FiUsers, FiFileText, FiCheckCircle, FiInfo } from "react-icons/fi";

const investmentServices = [
  { 
    icon: <FiHome className="text-white" size={32} />, 
    title: "Inversiones Inmobiliarias", 
    desc: "Proyectos residenciales, comerciales e industriales con alta rentabilidad y seguridad jurídica.",
    roi: "4% - 7%",
    risk: "Bajo",
    category: "real-estate"
  },
  { 
    icon: <FiTrendingUp className="text-white" size={32} />, 
    title: "Fondos de Inversión en Acciones", 
    desc: "Diversificación en mercados internacionales con gestión profesional y estrategias probadas.",
    roi: "8-12%",
    risk: "Medio",
    category: "stocks"
  },
  { 
    icon: <FiActivity className="text-white" size={32} />, 
    title: "Trading de Criptomonedas", 
    desc: "Fondos especializados en criptoactivos con estrategias algorítmicas y gestión activa.",
    roi: "5-10%",
    risk: "Alto",
    category: "crypto"
  },
  { 
    icon: <FiBarChart2 className="text-white" size={32} />, 
    title: "Trading Tradicional", 
    desc: "Operaciones en Forex, commodities y derivados con tecnología de vanguardia.",
    roi: "8%-12%",
    risk: "Medio-Alto",
    category: "trading"
  },
];

const detailedOpportunities = [
  {
    title: "Inversiones Inmobiliarias Premium",
    category: "Inmobiliario",
    roi: "4% - 7%",
    minInvestment: "$50,000 USD",
    duration: "18-36 meses",
    status: "Disponible",
    image: "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80",
    description: "Participación en proyectos inmobiliarios de alta gama en ubicaciones estratégicas de Bogotá, Medellín y Cali. Incluye desarrollos residenciales, comerciales e industriales con garantías jurídicas.",
    features: [
      "Escrituración inmediata de la inversión",
      "Seguros de responsabilidad civil y todo riesgo", 
      "Avalúos independientes trimestrales",
      "Opción de salida anticipada después de 12 meses",
      "Participación en plusvalía del proyecto"
    ],
    requirements: [
      "Inversión mínima: $50,000 USD",
      "Perfil de riesgo: Conservador a moderado",
      "Documentación: Declaración de renta último año",
      "Origen de fondos: Certificación bancaria",
      "Tiempo de vinculación: 18-36 meses"
    ],
    process: [
      "1. Evaluación del perfil de inversión",
      "2. Presentación de proyectos disponibles",
      "3. Due diligence legal y técnico",
      "4. Firma de contrato de participación",
      "5. Desembolso y inicio de proyecto",
      "6. Reportes mensuales de avance",
      "7. Liquidación y distribución de utilidades"
    ],
    legalAspects: [
      "Contrato de participación en fideicomiso",
      "Póliza de cumplimiento del constructor",
      "Licencias de construcción vigentes",
      "Estudios de suelos y factibilidad",
      "Seguros de todo riesgo del proyecto"
    ]
  },
  {
    title: "Fondos de Inversión Diversificados",
    category: "Acciones",
    roi: "8-12%",
    minInvestment: "$10,000 USD",
    duration: "12-24 meses",
    status: "Últimas plazas",
    image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=400&q=80",
    description: "Portafolios diversificados en mercados internacionales con énfasis en empresas tecnológicas, energías renovables y consumo masivo. Gestión profesional con estrategias probadas.",
    features: [
      "Diversificación en +100 empresas globales",
      "Rebalanceo automático mensual del portafolio",
      "Acceso a mercados estadounidenses y europeos",
      "Reportes detallados de performance mensual",
      "Liquidez parcial trimestral (hasta 30%)"
    ],
    requirements: [
      "Inversión mínima: $10,000 USD",
      "Perfil de riesgo: Moderado a agresivo",
      "Conocimiento del mercado de valores",
      "Capacidad de pérdida del 15% anual",
      "Horizonte de inversión mínimo: 12 meses"
    ],
    process: [
      "1. Test de perfil de riesgo (MIFID II)",
      "2. Selección de estrategia de inversión",
      "3. Apertura de cuenta en custodia internacional",
      "4. Transferencia de fondos y compra de participaciones",
      "5. Monitoreo y reportes mensuales",
      "6. Opción de reinversión de dividendos",
      "7. Liquidación según términos acordados"
    ],
    legalAspects: [
      "Regulación de la Superintendencia Financiera",
      "Custodia en entidades internacionales AAA",
      "Seguros de patrimonio autónomo",
      "Auditorías independientes semestrales",
      "Transparencia total en operaciones"
    ]
  },
  {
    title: "Trading de Criptoactivos",
    category: "Criptomonedas",
    roi: "5-10%",
    minInvestment: "$5,000 USD",
    duration: "6-18 meses",
    status: "Alta demanda",
    image: "https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=400&q=80",
    description: "Estrategias algorítmicas en el mercado de criptomonedas con enfoque en Bitcoin, Ethereum y altcoins seleccionadas. Incluye staking, yield farming y arbitraje automatizado.",
    features: [
      "Trading algorítmico 24/7 con IA",
      "Diversificación en +20 criptomonedas",
      "Staking automático en protocolos DeFi",
      "Arbitraje entre exchanges principales",
      "Stop-loss automático para protección"
    ],
    requirements: [
      "Inversión mínima: $5,000 USD",
      "Perfil de riesgo: Agresivo",
      "Tolerancia alta a la volatilidad",
      "Conocimiento básico de criptomonedas",
      "Capacidad de pérdida del 30% anual"
    ],
    process: [
      "1. Educación en fundamentos cripto",
      "2. Evaluación de tolerancia al riesgo",
      "3. Configuración de wallet institucional",
      "4. Implementación de estrategias algorítmicas",
      "5. Monitoreo en tiempo real 24/7",
      "6. Reportes semanales de performance",
      "7. Liquidación según mercado y términos"
    ],
    legalAspects: [
      "Custodia en cold wallets multi-firma",
      "Seguros contra hacks y robos",
      "Compliance con regulaciones locales",
      "Auditorías de smart contracts",
      "Transparencia en operaciones blockchain"
    ]
  },
  {
    title: "Trading Profesional Forex",
    category: "Trading",
    roi: "8%-12%",
    minInvestment: "$25,000 USD", 
    duration: "12-24 meses",
    status: "Disponible",
    image: "https://images.unsplash.com/photo-1590736969955-71cc94901144?auto=format&fit=crop&w=400&q=80",
    description: "Operaciones en mercado Forex, commodities y derivados con tecnología de alta frecuencia. Gestión de riesgo avanzada y estrategias institucionales probadas.",
    features: [
      "Trading de alta frecuencia (HFT)",
      "Análisis técnico y fundamental profesional",
      "Diversificación en múltiples pares de divisas",
      "Risk management automático",
      "Ejecución en microsegundos"
    ],
    requirements: [
      "Inversión mínima: $25,000 USD",
      "Perfil de riesgo: Moderado a agresivo",
      "Experiencia previa en trading",
      "Capacidad de drawdown del 12%",
      "Comprensión del apalancamiento financiero"
    ],
    process: [
      "1. Evaluación de experiencia en trading",
      "2. Configuración de cuenta segregada",
      "3. Implementación de algoritmos de trading",
      "4. Ejecución automatizada de estrategias",
      "5. Monitoreo de riesgo en tiempo real",
      "6. Reportes diarios de operaciones",
      "7. Liquidación y distribución de ganancias"
    ],
    legalAspects: [
      "Regulación de brokers internacionales",
      "Cuentas segregadas en bancos Tier 1",
      "Seguros de responsabilidad profesional",
      "Auditorías de estrategias de trading",
      "Transparencia total en operaciones"
    ]
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
    desc: "Equipo de expertos con más de 6 años de experiencia"
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

  const whatsappNumber = "+573166827239"; // Número de WhatsApp de la entidad
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
                        <p className="text-gray-300 text-sm mb-4 leading-relaxed">{opportunity.description}</p>
                        
                        {/* Features */}
                        <div className="mb-4">
                          <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <FiCheckCircle size={16} />
                            Características principales:
                          </h4>
                          <ul className="space-y-1">
                            {opportunity.features.map((feature, i) => (
                              <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                {feature}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Requirements */}
                        <div className="mb-4">
                          <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <FiFileText size={16} />
                            Requisitos:
                          </h4>
                          <ul className="space-y-1">
                            {opportunity.requirements.map((req, i) => (
                              <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                                {req}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Process */}
                        <div className="mb-4">
                          <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <FiClock size={16} />
                            Proceso de inversión:
                          </h4>
                          <ul className="space-y-1">
                            {opportunity.process.map((step, i) => (
                              <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                                <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-2"></div>
                                {step}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Legal Aspects */}
                        <div className="mb-4">
                          <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <FiShield size={16} />
                            Aspectos legales y seguridad:
                          </h4>
                          <ul className="space-y-1">
                            {opportunity.legalAspects.map((legal, i) => (
                              <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-purple-500 rounded-full"></div>
                                {legal}
                              </li>
                            ))}
                          </ul>
                        </div>
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

        {/* Partners Carousel */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-4">Nuestros Aliados Estratégicos</h2>
            <p className="text-gray-300">Trabajamos con las mejores instituciones financieras y tecnológicas del mundo</p>
          </div>
          
          <div className="relative overflow-hidden py-8">
            <div className="flex animate-scroll whitespace-nowrap">
              {/* Primera fila de logos */}
              <div className="flex items-center gap-16 shrink-0">
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Goldman<br/>Sachs</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">JP<br/>Morgan</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">BlackRock</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Binance</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Visa</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Mastercard</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Microsoft</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Amazon</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Tesla</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Apple</span>
                </div>
              </div>
              
              {/* Segunda fila idéntica para el efecto infinito */}
              <div className="flex items-center gap-16 shrink-0 ml-16">
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Goldman<br/>Sachs</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">JP<br/>Morgan</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">BlackRock</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Binance</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Visa</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Mastercard</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Microsoft</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Amazon</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Tesla</span>
                </div>
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform duration-300">
                  <span className="text-gray-800 font-bold text-sm text-center">Apple</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Why Choose Us */}
        <div className="bg-gray-900 rounded-2xl p-12 text-center border border-gray-700">
          <div className="flex items-center justify-center gap-3 mb-6">
            <FiAward className="text-white text-3xl" />
            <h2 className="text-4xl font-bold text-white">¿Por qué GENIUS INDUSTRIES?</h2>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8 mt-12">
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">+324</div>
              <p className="text-gray-300">Proyectos exitosos</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">$150M+</div>
              <p className="text-gray-300">Capital gestionado</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">6 años</div>
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

export const Route = createFileRoute('/investment')({
  component: InvestmentPage,
}); 
