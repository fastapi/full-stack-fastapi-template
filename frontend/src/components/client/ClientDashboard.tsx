import React, { useState, useEffect } from "react";
import { FiHome, FiDollarSign, FiTrendingUp, FiCreditCard, FiEye, FiHeart, FiCalendar, FiBarChart, FiPieChart, FiSettings, FiDownload, FiPlus, FiEdit3, FiTrash2, FiMapPin, FiUser, FiPhone, FiMail } from "react-icons/fi";

interface Property {
  id: string;
  title: string;
  type: string;
  location: string;
  price: number;
  currency: string;
  transactionType: "venta" | "alquiler";
  status: "disponible" | "vendido" | "alquilado" | "retirado";
  listingDate: string;
  views: number;
  favorites: number;
  monthlyIncome?: number; // Para alquileres
  agent: {
    name: string;
    phone: string;
    email: string;
  };
}

interface Credit {
  id: string;
  type: string;
  amount: number;
  currency: string;
  status: "aprobado" | "pendiente" | "rechazado" | "pagado";
  monthlyPayment: number;
  remainingBalance: number;
  nextPaymentDate: string;
  term: number;
  interestRate: number;
}

interface Investment {
  id: string;
  type: string;
  amount: number;
  currency: string;
  roi: number;
  status: "activo" | "completado" | "cancelado";
  startDate: string;
  endDate?: string;
  monthlyReturn: number;
}

interface ClientMetrics {
  totalPropertyValue: number;
  monthlyRentalIncome: number;
  totalCredits: number;
  totalInvestments: number;
  netWorth: number;
  portfolioGrowth: number;
}

// Datos de ejemplo - en producción vendrían de la API
const sampleProperties: Property[] = [
  {
    id: "1",
    title: "Apartamento El Poblado",
    type: "Apartamento",
    location: "El Poblado, Medellín",
    price: 650000000,
    currency: "COP",
    transactionType: "alquiler",
    status: "alquilado",
    listingDate: "2024-01-15",
    views: 245,
    favorites: 12,
    monthlyIncome: 3200000,
    agent: {
      name: "Ana López",
      phone: "+57 316 682 7239",
      email: "ana@geniusindustries.org"
    }
  },
  {
    id: "2",
    title: "Casa Zona Rosa",
    type: "Casa",
    location: "Zona Rosa, Bogotá",
    price: 850000000,
    currency: "COP",
    transactionType: "venta",
    status: "vendido",
    listingDate: "2023-12-10",
    views: 412,
    favorites: 28,
    agent: {
      name: "Carlos Martínez",
      phone: "+57 316 682 7239",
      email: "carlos@geniusindustries.org"
    }
  }
];

const sampleCredits: Credit[] = [
  {
    id: "1",
    type: "Hipotecario",
    amount: 420000000,
    currency: "COP",
    status: "aprobado",
    monthlyPayment: 2850000,
    remainingBalance: 385000000,
    nextPaymentDate: "2024-02-15",
    term: 180,
    interestRate: 1.2
  },
  {
    id: "2",
    type: "Personal",
    amount: 50000000,
    currency: "COP",
    status: "pagado",
    monthlyPayment: 0,
    remainingBalance: 0,
    nextPaymentDate: "-",
    term: 36,
    interestRate: 2.5
  }
];

const sampleInvestments: Investment[] = [
  {
    id: "1",
    type: "Fondo Inmobiliario",
    amount: 100000000,
    currency: "COP",
    roi: 8.5,
    status: "activo",
    startDate: "2023-06-01",
    monthlyReturn: 708333
  },
  {
    id: "2",
    type: "Trading Tradicional",
    amount: 25000000,
    currency: "COP",
    roi: 12.3,
    status: "activo",
    startDate: "2023-09-15",
    monthlyReturn: 256250
  }
];

const ClientDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [properties, setProperties] = useState<Property[]>(sampleProperties);
  const [credits, setCredits] = useState<Credit[]>(sampleCredits);
  const [investments, setInvestments] = useState<Investment[]>(sampleInvestments);
  const [metrics, setMetrics] = useState<ClientMetrics>({
    totalPropertyValue: 0,
    monthlyRentalIncome: 0,
    totalCredits: 0,
    totalInvestments: 0,
    netWorth: 0,
    portfolioGrowth: 12.5
  });

  useEffect(() => {
    // Calcular métricas
    const totalPropertyValue = properties.reduce((sum, prop) => sum + prop.price, 0);
    const monthlyRentalIncome = properties
      .filter(prop => prop.transactionType === "alquiler" && prop.status === "alquilado")
      .reduce((sum, prop) => sum + (prop.monthlyIncome || 0), 0);
    const totalCredits = credits.reduce((sum, credit) => sum + credit.remainingBalance, 0);
    const totalInvestments = investments.reduce((sum, inv) => sum + inv.amount, 0);
    const netWorth = totalPropertyValue + totalInvestments - totalCredits;

    setMetrics({
      totalPropertyValue,
      monthlyRentalIncome,
      totalCredits,
      totalInvestments,
      netWorth,
      portfolioGrowth: 12.5
    });
  }, [properties, credits, investments]);

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    const colors = {
      "disponible": "bg-blue-100 text-blue-800",
      "vendido": "bg-green-100 text-green-800",
      "alquilado": "bg-purple-100 text-purple-800",
      "retirado": "bg-red-100 text-red-800",
      "aprobado": "bg-green-100 text-green-800",
      "pendiente": "bg-yellow-100 text-yellow-800",
      "rechazado": "bg-red-100 text-red-800",
      "pagado": "bg-gray-100 text-gray-800",
      "activo": "bg-green-100 text-green-800",
      "completado": "bg-blue-100 text-blue-800",
      "cancelado": "bg-red-100 text-red-800"
    };
    return colors[status as keyof typeof colors] || "bg-gray-100 text-gray-800";
  };

  const tabs = [
    { id: "overview", label: "Resumen", icon: FiBarChart },
    { id: "properties", label: "Propiedades", icon: FiHome },
    { id: "credits", label: "Créditos", icon: FiCreditCard },
    { id: "investments", label: "Inversiones", icon: FiTrendingUp },
    { id: "reports", label: "Reportes", icon: FiPieChart }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard Cliente</h1>
          <p className="text-gray-600">Gestiona tus propiedades, créditos e inversiones</p>
        </div>

        {/* Tabs Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'border-black text-black'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-8">
            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <FiHome className="text-green-600" size={24} />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">Valor Propiedades</h3>
                    <p className="text-2xl font-semibold text-gray-900">
                      {formatCurrency(metrics.totalPropertyValue, "COP")}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <FiDollarSign className="text-blue-600" size={24} />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">Ingresos Mensuales</h3>
                    <p className="text-2xl font-semibold text-gray-900">
                      {formatCurrency(metrics.monthlyRentalIncome, "COP")}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <FiCreditCard className="text-purple-600" size={24} />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">Deuda Total</h3>
                    <p className="text-2xl font-semibold text-gray-900">
                      {formatCurrency(metrics.totalCredits, "COP")}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 bg-yellow-100 rounded-lg">
                    <FiTrendingUp className="text-yellow-600" size={24} />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-sm font-medium text-gray-500">Patrimonio Neto</h3>
                    <p className="text-2xl font-semibold text-gray-900">
                      {formatCurrency(metrics.netWorth, "COP")}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Crecimiento del Portafolio</h3>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <FiTrendingUp className="mx-auto text-green-500 mb-2" size={48} />
                    <p className="text-3xl font-bold text-green-500">+{metrics.portfolioGrowth}%</p>
                    <p className="text-gray-600">Este año</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución de Activos</h3>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <FiPieChart className="mx-auto text-blue-500 mb-2" size={48} />
                    <p className="text-gray-600">Gráfico de distribución</p>
                    <p className="text-sm text-gray-500">Propiedades • Inversiones • Créditos</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg mr-3">
                      <FiDollarSign className="text-green-600" size={16} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Pago de alquiler recibido</p>
                      <p className="text-sm text-gray-500">Apartamento El Poblado - Hace 2 días</p>
                    </div>
                  </div>
                  <span className="text-green-600 font-semibold">+$3,200,000</span>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg mr-3">
                      <FiTrendingUp className="text-blue-600" size={16} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Retorno de inversión</p>
                      <p className="text-sm text-gray-500">Fondo Inmobiliario - Hace 1 semana</p>
                    </div>
                  </div>
                  <span className="text-blue-600 font-semibold">+$708,333</span>
                </div>

                <div className="flex items-center justify-between py-3">
                  <div className="flex items-center">
                    <div className="p-2 bg-red-100 rounded-lg mr-3">
                      <FiCreditCard className="text-red-600" size={16} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Pago de crédito hipotecario</p>
                      <p className="text-sm text-gray-500">Hace 2 semanas</p>
                    </div>
                  </div>
                  <span className="text-red-600 font-semibold">-$2,850,000</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Properties Tab */}
        {activeTab === "properties" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Mis Propiedades</h2>
              <button className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2">
                <FiPlus size={16} />
                Agregar Propiedad
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {properties.map((property) => (
                <div key={property.id} className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{property.title}</h3>
                        <p className="text-gray-600 flex items-center gap-1">
                          <FiMapPin size={14} />
                          {property.location}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button className="p-2 text-gray-400 hover:text-gray-600">
                          <FiEdit3 size={16} />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-600">
                          <FiTrash2 size={16} />
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Precio</p>
                        <p className="font-semibold text-gray-900">
                          {formatCurrency(property.price, property.currency)}
                          {property.transactionType === "alquiler" && "/mes"}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Estado</p>
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(property.status)}`}>
                          {property.status}
                        </span>
                      </div>
                    </div>

                    {property.monthlyIncome && (
                      <div className="mb-4">
                        <p className="text-sm text-gray-500">Ingresos Mensuales</p>
                        <p className="font-semibold text-green-600">
                          {formatCurrency(property.monthlyIncome, property.currency)}
                        </p>
                      </div>
                    )}

                    <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                      <span className="flex items-center gap-1">
                        <FiEye size={14} />
                        {property.views} vistas
                      </span>
                      <span className="flex items-center gap-1">
                        <FiHeart size={14} />
                        {property.favorites} favoritos
                      </span>
                      <span className="flex items-center gap-1">
                        <FiCalendar size={14} />
                        {formatDate(property.listingDate)}
                      </span>
                    </div>

                    <div className="border-t border-gray-200 pt-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <FiUser size={14} className="text-gray-400" />
                          <span className="text-sm text-gray-600">{property.agent.name}</span>
                        </div>
                        <div className="flex gap-2">
                          <a
                            href={`tel:${property.agent.phone}`}
                            className="p-2 text-gray-400 hover:text-green-600"
                          >
                            <FiPhone size={14} />
                          </a>
                          <a
                            href={`mailto:${property.agent.email}`}
                            className="p-2 text-gray-400 hover:text-blue-600"
                          >
                            <FiMail size={14} />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Credits Tab */}
        {activeTab === "credits" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Mis Créditos</h2>
              <button className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2">
                <FiPlus size={16} />
                Solicitar Crédito
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {credits.map((credit) => (
                <div key={credit.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Crédito {credit.type}</h3>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(credit.amount, credit.currency)}
                      </p>
                    </div>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(credit.status)}`}>
                      {credit.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Saldo Pendiente</p>
                      <p className="font-semibold text-red-600">
                        {formatCurrency(credit.remainingBalance, credit.currency)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Cuota Mensual</p>
                      <p className="font-semibold text-gray-900">
                        {formatCurrency(credit.monthlyPayment, credit.currency)}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Próximo Pago</p>
                      <p className="font-semibold text-gray-900">
                        {credit.nextPaymentDate !== "-" ? formatDate(credit.nextPaymentDate) : "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Tasa de Interés</p>
                      <p className="font-semibold text-gray-900">{credit.interestRate}%</p>
                    </div>
                  </div>

                  {credit.status === "aprobado" && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Progreso del pago</span>
                        <span className="font-medium text-gray-900">
                          {Math.round(((credit.amount - credit.remainingBalance) / credit.amount) * 100)}%
                        </span>
                      </div>
                      <div className="mt-2 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${((credit.amount - credit.remainingBalance) / credit.amount) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Investments Tab */}
        {activeTab === "investments" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Mis Inversiones</h2>
              <button className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2">
                <FiPlus size={16} />
                Nueva Inversión
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {investments.map((investment) => (
                <div key={investment.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{investment.type}</h3>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(investment.amount, investment.currency)}
                      </p>
                    </div>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(investment.status)}`}>
                      {investment.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">ROI</p>
                      <p className="font-semibold text-green-600">{investment.roi}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Retorno Mensual</p>
                      <p className="font-semibold text-green-600">
                        {formatCurrency(investment.monthlyReturn, investment.currency)}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Fecha de Inicio</p>
                      <p className="font-semibold text-gray-900">{formatDate(investment.startDate)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Duración</p>
                      <p className="font-semibold text-gray-900">
                        {investment.endDate ? `Hasta ${formatDate(investment.endDate)}` : "Indefinida"}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === "reports" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Reportes Financieros</h2>
              <button className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2">
                <FiDownload size={16} />
                Exportar Todo
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Estado de Cuenta</h3>
                  <FiDownload className="text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
                <p className="text-gray-600 mb-4">Resumen completo de todas tus finanzas</p>
                <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                  Generar Reporte
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Flujo de Caja</h3>
                  <FiDownload className="text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
                <p className="text-gray-600 mb-4">Ingresos y gastos mensuales detallados</p>
                <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                  Generar Reporte
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Performance de Inversiones</h3>
                  <FiDownload className="text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
                <p className="text-gray-600 mb-4">Análisis de rendimiento de tus inversiones</p>
                <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                  Generar Reporte
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Reporte Tributario</h3>
                  <FiDownload className="text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
                <p className="text-gray-600 mb-4">Información para declaración de impuestos</p>
                <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                  Generar Reporte
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Análisis de Portafolio</h3>
                  <FiDownload className="text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
                <p className="text-gray-600 mb-4">Diversificación y balance de activos</p>
                <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                  Generar Reporte
                </button>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Proyecciones Futuras</h3>
                  <FiDownload className="text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
                <p className="text-gray-600 mb-4">Estimaciones de crecimiento patrimonial</p>
                <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                  Generar Reporte
                </button>
              </div>
            </div>

            {/* Summary Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Resumen Financiero Anual</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    {formatCurrency(metrics.monthlyRentalIncome * 12, "COP")}
                  </p>
                  <p className="text-gray-600">Ingresos por Alquileres</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    {formatCurrency(investments.reduce((sum, inv) => sum + (inv.monthlyReturn * 12), 0), "COP")}
                  </p>
                  <p className="text-gray-600">Retorno de Inversiones</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-red-600">
                    {formatCurrency(credits.filter(c => c.status === "aprobado").reduce((sum, c) => sum + (c.monthlyPayment * 12), 0), "COP")}
                  </p>
                  <p className="text-gray-600">Pagos de Créditos</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">
                    {formatCurrency((metrics.monthlyRentalIncome * 12) + (investments.reduce((sum, inv) => sum + (inv.monthlyReturn * 12), 0)) - (credits.filter(c => c.status === "aprobado").reduce((sum, c) => sum + (c.monthlyPayment * 12), 0)), "COP")}
                  </p>
                  <p className="text-gray-600">Flujo Neto Anual</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClientDashboard; 