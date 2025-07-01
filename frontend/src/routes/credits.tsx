import React, { useState, useEffect } from "react";
import { createFileRoute } from '@tanstack/react-router';
import { FiDollarSign, FiClock, FiShield, FiActivity, FiCheck, FiInfo, FiPhone, FiMail, FiMapPin, FiArrowUpRight, FiPercent, FiTrendingUp, FiGlobe, FiFlag } from "react-icons/fi";

interface CreditSimulation {
  monthlyPayment: number;
  totalPayment: number;
  totalInterest: number;
  paymentTable: Array<{
    month: number;
    payment: number;
    principal: number;
    interest: number;
    balance: number;
  }>;
}

const countries = [
  {
    code: 'CO',
    name: 'Colombia',
    currency: 'COP',
    symbol: '$',
    flag: '🇨🇴',
    rates: {
      personal: { min: 2.2, max: 3.8 },
      business: { min: 1.8, max: 3.2 },
      mortgage: { min: 1.0, max: 1.8 },
      vehicle: { min: 1.5, max: 2.8 }
    }
  },
  {
    code: 'IT',
    name: 'Italia',
    currency: 'EUR',
    symbol: '€',
    flag: '🇮🇹',
    rates: {
      personal: { min: 1.5, max: 2.8 },
      business: { min: 1.2, max: 2.5 },
      mortgage: { min: 0.5, max: 1.2 },
      vehicle: { min: 0.8, max: 2.0 }
    }
  }
];

const getCreditTypes = (selectedCountry: any) => [
  {
    icon: <FiDollarSign className="text-white" size={32} />,
    title: "Crédito Personal",
    desc: "Para gastos personales, educación, viajes o cualquier necesidad. Sin garantías requeridas.",
    amount: selectedCountry.currency === 'EUR' ? '€5,000 - €80,000' : '$2,500,000 - $300,000,000 COP',
    term: "6 - 60 meses",
    rate: `${selectedCountry.rates.personal.min}% - ${selectedCountry.rates.personal.max}%`,
    category: "personal"
  },
  {
    icon: <FiTrendingUp className="text-white" size={32} />,
    title: "Crédito Empresarial",
    desc: "Capital de trabajo, expansión de negocio o nuevos proyectos empresariales.",
    amount: selectedCountry.currency === 'EUR' ? '€10,000 - €400,000' : '$30,000,000 - $1,500,000,000 COP',
    term: "12 - 84 meses",
    rate: `${selectedCountry.rates.business.min}% - ${selectedCountry.rates.business.max}%`,
    category: "business"
  },
  {
    icon: <FiShield className="text-white" size={32} />,
    title: "Crédito Hipotecario",
    desc: "Para compra de vivienda nueva o usada con las mejores tasas del mercado.",
    amount: selectedCountry.currency === 'EUR' ? '€50,000 - €1,500,000' : '$150,000,000 - $4,500,000,000 COP',
    term: "60 - 360 meses",
    rate: `${selectedCountry.rates.mortgage.min}% - ${selectedCountry.rates.mortgage.max}%`,
    category: "mortgage"
  },
  {
    icon: <FiPercent className="text-white" size={32} />,
    title: "Crédito Vehículo",
    desc: "Financiación para vehículos nuevos y usados con cuotas fijas.",
    amount: selectedCountry.currency === 'EUR' ? '€8,000 - €150,000' : '$25,000,000 - $450,000,000 COP',
    term: "12 - 72 meses",
    rate: `${selectedCountry.rates.vehicle.min}% - ${selectedCountry.rates.vehicle.max}%`,
    category: "vehicle"
  },
];

const benefits = [
  { 
    icon: <FiClock className="text-white" size={28} />, 
    title: "Aprobación Rápida", 
    desc: "Respuesta en 24-48 horas con documentación completa"
  },
  { 
    icon: <FiDollarSign className="text-white" size={28} />, 
    title: "Tasas Competitivas", 
    desc: "Las mejores tasas del mercado con capital propio"
  },
  { 
    icon: <FiShield className="text-white" size={28} />, 
    title: "Sin Comisiones Ocultas", 
    desc: "Transparencia total en costos y comisiones"
  },
  { 
    icon: <FiCheck className="text-white" size={28} />, 
    title: "Flexibilidad", 
    desc: "Planes de pago adaptados a tu capacidad"
  },
];

const faqs = [
  {
    question: "¿Qué documentos necesito para solicitar un crédito?",
    answer: "Cédula de ciudadanía, declaración de renta último año, certificados de ingresos, referencias comerciales y personales, y para hipotecarios: avalúo del inmueble."
  },
  {
    question: "¿Cuál es el tiempo de aprobación?",
    answer: "Con documentación completa, nuestro tiempo de respuesta es de 24 a 48 horas para créditos personales y hasta 5 días hábiles para créditos hipotecarios."
  },
  {
    question: "¿Puedo hacer pagos anticipados?",
    answer: "Sí, aceptamos pagos anticipados sin penalización. Esto reduce el capital adeudado y los intereses futuros."
  },
  {
    question: "¿Qué pasa si tengo dificultades de pago?",
    answer: "Contamos con planes de reestructuración y refinanciación. Contáctanos antes de tener retrasos para encontrar la mejor solución."
  },
  {
    question: "¿Los créditos están respaldados por qué entidad?",
    answer: "Todos nuestros créditos son otorgados con capital propio de GENIUS INDUSTRIES, respaldados por nuestro patrimonio y trayectoria de 6 años en el mercado."
  },
];

function CreditsPage() {
  const [selectedCountry, setSelectedCountry] = useState(countries[0]); // Colombia por defecto
  const [selectedCreditType, setSelectedCreditType] = useState('personal');
  const [loanAmount, setLoanAmount] = useState(2500000); // Monto mínimo para Colombia
  const [loanTerm, setLoanTerm] = useState(24);
  const [interestRate, setInterestRate] = useState(2.5);
  const [simulation, setSimulation] = useState<CreditSimulation | null>(null);
  const [showPaymentTable, setShowPaymentTable] = useState(false);
  
  // Estados para el modal y formulario
  const [showModal, setShowModal] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    idNumber: '',
    monthlyIncome: '',
    employmentType: '',
    creditType: 'personal',
    requestedAmount: '',
    purpose: '',
    hasCollateral: false,
    collateralDescription: ''
  });

  const whatsappNumber = "+573166827239";
  const whatsappMessage = "Hola, me interesa obtener información sobre los créditos de GENIUS INDUSTRIES. ¿Podrían asesorarme?";
  const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(whatsappMessage)}`;

  const creditTypes = getCreditTypes(selectedCountry);

  const navigateToSimulator = (creditCategory: string) => {
    setSelectedCreditType(creditCategory);
    // Ajustar la tasa de interés según el tipo de crédito y país
    const rates = selectedCountry.rates[creditCategory as keyof typeof selectedCountry.rates];
    setInterestRate((rates.min + rates.max) / 2);
    
    // Navegar al simulador
    setTimeout(() => {
      document.getElementById('simulator')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Enviar solicitud al backend
      const applicationData = {
        ...formData,
        country: selectedCountry.name,
        currency: selectedCountry.currency
      };

      const response = await fetch('http://localhost:8000/api/v1/credits/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(applicationData),
      });

      if (!response.ok) {
        throw new Error('Error al enviar la solicitud');
      }

      const result = await response.json();
      
      alert(`¡Solicitud enviada exitosamente a creditos@geniusindustries.org! 
      
ID de Aplicación: ${result.application_id}

✅ ${result.message}

📧 Email enviado a: ${result.email_sent_to || 'creditos@geniusindustries.org'}

Próximos pasos:
${result.next_steps ? result.next_steps.map((step: string, index: number) => `${index + 1}. ${step}`).join('\n') : '• Te contactaremos pronto por WhatsApp y email'}

¡Gracias por confiar en GENIUS INDUSTRIES!`);
      
      // Reset form
      setFormData({
        fullName: '',
        email: '',
        phone: '',
        idNumber: '',
        monthlyIncome: '',
        employmentType: '',
        creditType: 'personal',
        requestedAmount: '',
        purpose: '',
        hasCollateral: false,
        collateralDescription: ''
      });
      setShowForm(false);
      setShowModal(false);
      
    } catch (error) {
      console.error('Error:', error);
      alert('Error al enviar la solicitud. Por favor intenta nuevamente o contáctanos por WhatsApp.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const calculateCredit = () => {
    const monthlyRate = interestRate / 100 / 12;
    const monthlyPayment = (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, loanTerm)) / 
                          (Math.pow(1 + monthlyRate, loanTerm) - 1);
    
    const totalPayment = monthlyPayment * loanTerm;
    const totalInterest = totalPayment - loanAmount;
    
    // Tabla de amortización
    const paymentTable = [];
    let balance = loanAmount;
    
    for (let month = 1; month <= loanTerm; month++) {
      const interestPayment = balance * monthlyRate;
      const principalPayment = monthlyPayment - interestPayment;
      balance -= principalPayment;
      
      paymentTable.push({
        month,
        payment: monthlyPayment,
        principal: principalPayment,
        interest: interestPayment,
        balance: Math.max(balance, 0)
      });
    }
    
    setSimulation({
      monthlyPayment,
      totalPayment,
      totalInterest,
      paymentTable
    });
  };

  useEffect(() => {
    calculateCredit();
  }, [loanAmount, loanTerm, interestRate]);

  // Ajustar monto cuando cambie el país
  useEffect(() => {
    if (selectedCountry.currency === 'EUR' && loanAmount > 500000) {
      setLoanAmount(25000); // Monto apropiado para EUR
    } else if (selectedCountry.currency === 'COP' && loanAmount < 2500000) {
      setLoanAmount(2500000); // Monto mínimo para COP
    }
  }, [selectedCountry]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat(selectedCountry.code === 'CO' ? 'es-CO' : 'it-IT', {
      style: 'currency',
      currency: selectedCountry.currency
    }).format(amount);
  };

  return (
    <div className="bg-black min-h-screen py-16 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6">
            Créditos GENIUS INDUSTRIES
          </h1>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto mb-8">
            Financiamos tus sueños con capital propio. Créditos personales, empresariales, 
            hipotecarios y vehiculares con las mejores tasas y condiciones del mercado.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => setShowModal(true)}
              className="bg-white text-black font-semibold py-4 px-8 rounded-lg hover:bg-gray-200 transform hover:scale-105 transition-all duration-200 shadow-lg flex items-center gap-2"
            >
              <FiPhone size={20} />
              Solicitar Crédito
            </button>
            <button 
              onClick={() => document.getElementById('simulator')?.scrollIntoView({ behavior: 'smooth' })}
              className="border-2 border-white text-white font-semibold py-4 px-8 rounded-lg hover:bg-white hover:text-black transition-all duration-200 flex items-center gap-2"
            >
              <FiActivity size={20} />
              Usar Simulador
            </button>
          </div>
        </div>

        {/* Country Selection */}
        <div className="mb-16">
          <div className="bg-gray-900 rounded-2xl p-8 border border-gray-700">
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold text-white mb-4 flex items-center justify-center gap-3">
                <FiGlobe className="text-white" />
                Selecciona tu País
              </h2>
              <p className="text-gray-300">Elige tu ubicación para ver las tasas y monedas locales</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
              {countries.map((country) => (
                <button
                  key={country.code}
                  onClick={() => setSelectedCountry(country)}
                  className={`p-6 rounded-xl border-2 transition-all duration-300 ${
                    selectedCountry.code === country.code
                      ? 'border-white bg-gray-800'
                      : 'border-gray-600 bg-gray-800 hover:border-gray-500'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-4xl mb-2">{country.flag}</div>
                    <h3 className="text-xl font-bold text-white mb-2">{country.name}</h3>
                    <p className="text-gray-300 text-sm">Moneda: {country.currency}</p>
                    <p className="text-gray-400 text-xs mt-1">Tasas desde {Math.min(...Object.values(country.rates).map(r => r.min))}%</p>
                  </div>
                </button>
              ))}
            </div>
            
            <div className="text-center mt-6">
              <p className="text-gray-400 text-sm">
                País seleccionado: <span className="text-white font-semibold">{selectedCountry.name}</span> | 
                Moneda: <span className="text-white font-semibold">{selectedCountry.currency}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Credit Types */}
        <div className="mb-16">
          <h2 className="text-4xl font-bold text-white mb-12 text-center">Tipos de Crédito Disponibles</h2>
          <div className="grid lg:grid-cols-2 gap-8">
            {creditTypes.map((credit, index) => (
              <div key={index} className="bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-700 hover:border-gray-600 transition-all duration-300 group">
                <div className="flex items-start justify-between mb-6">
                  <div className="p-4 bg-gray-700 rounded-xl group-hover:scale-110 transition-transform duration-300">
                    {credit.icon}
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400 mb-1">Tasa desde</div>
                    <div className="text-xl font-bold text-white">{credit.rate}</div>
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{credit.title}</h3>
                <p className="text-gray-300 leading-relaxed mb-6">{credit.desc}</p>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <div className="text-gray-400 text-sm">Monto</div>
                    <div className="text-white font-semibold">{credit.amount}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Plazo</div>
                    <div className="text-white font-semibold">{credit.term}</div>
                  </div>
                </div>
                <button 
                  onClick={() => navigateToSimulator(credit.category)}
                  className="w-full bg-white text-black font-semibold py-3 px-4 rounded-lg hover:bg-gray-200 transition-all duration-200"
                >
                  Simular este crédito
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Credit Simulator */}
        <div id="simulator" className="mb-16">
          <div className="bg-gray-900 rounded-2xl p-8 border border-gray-700">
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold text-white mb-4 flex items-center justify-center gap-3">
                <FiActivity className="text-white" />
                Simulador de Créditos
              </h2>
              <p className="text-xl text-gray-300">Calcula tu cuota mensual y plan de pagos en {selectedCountry.currency}</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              {/* Input Form */}
              <div className="space-y-6">
                <div>
                  <label className="block text-white font-semibold mb-2">Tipo de Crédito</label>
                  <select 
                    value={selectedCreditType}
                    onChange={(e) => {
                      setSelectedCreditType(e.target.value);
                      const rates = selectedCountry.rates[e.target.value as keyof typeof selectedCountry.rates];
                      setInterestRate((rates.min + rates.max) / 2);
                    }}
                    className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-3 focus:border-white focus:outline-none"
                  >
                    <option value="personal">Crédito Personal ({selectedCountry.rates.personal.min}% - {selectedCountry.rates.personal.max}%)</option>
                    <option value="business">Crédito Empresarial ({selectedCountry.rates.business.min}% - {selectedCountry.rates.business.max}%)</option>
                    <option value="mortgage">Crédito Hipotecario ({selectedCountry.rates.mortgage.min}% - {selectedCountry.rates.mortgage.max}%)</option>
                    <option value="vehicle">Crédito Vehículo ({selectedCountry.rates.vehicle.min}% - {selectedCountry.rates.vehicle.max}%)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Monto del Crédito: {formatCurrency(loanAmount)}
                  </label>
                  <input
                    type="range"
                    min={selectedCountry.currency === 'EUR' ? "5000" : "2500000"}
                    max={selectedCountry.currency === 'EUR' ? "500000" : "1500000000"}
                    step={selectedCountry.currency === 'EUR' ? "1000" : "1000000"}
                    value={loanAmount}
                    onChange={(e) => setLoanAmount(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-gray-400 text-sm mt-1">
                    <span>{selectedCountry.currency === 'EUR' ? '€5,000' : '$2,500,000 COP'}</span>
                    <span>{selectedCountry.currency === 'EUR' ? '€500,000' : '$1,500,000,000 COP'}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Plazo: {loanTerm} meses
                  </label>
                  <input
                    type="range"
                    min="6"
                    max="360"
                    step="6"
                    value={loanTerm}
                    onChange={(e) => setLoanTerm(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-gray-400 text-sm mt-1">
                    <span>6 meses</span>
                    <span>360 meses</span>
                  </div>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Tasa de Interés Mensual: {interestRate}%
                  </label>
                  <input
                    type="range"
                    min={selectedCountry.rates[selectedCreditType as keyof typeof selectedCountry.rates]?.min || 0.8}
                    max={selectedCountry.rates[selectedCreditType as keyof typeof selectedCountry.rates]?.max || 3.5}
                    step="0.1"
                    value={interestRate}
                    onChange={(e) => setInterestRate(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-gray-400 text-sm mt-1">
                    <span>{selectedCountry.rates[selectedCreditType as keyof typeof selectedCountry.rates]?.min || 0.8}%</span>
                    <span>{selectedCountry.rates[selectedCreditType as keyof typeof selectedCountry.rates]?.max || 3.5}%</span>
                  </div>
                </div>
              </div>

              {/* Results */}
              <div className="space-y-6">
                {simulation && (
                  <>
                    <div className="bg-gray-800 rounded-xl p-6">
                      <h3 className="text-xl font-bold text-white mb-4">Resumen del Crédito</h3>
                      <div className="space-y-4">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Cuota Mensual:</span>
                          <span className="text-white font-bold text-xl">
                            {formatCurrency(simulation.monthlyPayment)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Total a Pagar:</span>
                          <span className="text-white font-semibold">
                            {formatCurrency(simulation.totalPayment)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Total Intereses:</span>
                          <span className="text-white font-semibold">
                            {formatCurrency(simulation.totalInterest)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Monto del Crédito:</span>
                          <span className="text-white font-semibold">
                            {formatCurrency(loanAmount)}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => setShowPaymentTable(!showPaymentTable)}
                        className="flex-1 bg-white text-black font-semibold py-3 px-4 rounded-lg hover:bg-gray-200 transition-all duration-200"
                      >
                        {showPaymentTable ? 'Ocultar Tabla' : 'Ver Tabla de Pagos'}
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
                  </>
                )}
              </div>
            </div>

            {/* Payment Table */}
            {showPaymentTable && simulation && (
              <div className="mt-8">
                <h3 className="text-xl font-bold text-white mb-4">Tabla de Amortización</h3>
                <div className="overflow-x-auto">
                  <table className="w-full bg-gray-800 rounded-lg">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left text-gray-300 p-3">Mes</th>
                        <th className="text-left text-gray-300 p-3">Cuota</th>
                        <th className="text-left text-gray-300 p-3">Capital</th>
                        <th className="text-left text-gray-300 p-3">Interés</th>
                        <th className="text-left text-gray-300 p-3">Saldo</th>
                      </tr>
                    </thead>
                    <tbody>
                      {simulation.paymentTable.slice(0, 12).map((payment) => (
                        <tr key={payment.month} className="border-b border-gray-700">
                          <td className="text-white p-3">{payment.month}</td>
                          <td className="text-white p-3">{formatCurrency(payment.payment)}</td>
                          <td className="text-white p-3">{formatCurrency(payment.principal)}</td>
                          <td className="text-white p-3">{formatCurrency(payment.interest)}</td>
                          <td className="text-white p-3">{formatCurrency(payment.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {simulation.paymentTable.length > 12 && (
                    <p className="text-gray-400 text-sm mt-2 text-center">
                      Mostrando primeros 12 meses de {simulation.paymentTable.length} total
                    </p>
                  )}
                </div>
              </div>
            )}
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

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-4xl font-bold text-white mb-12 text-center">Preguntas Frecuentes</h2>
          <div className="grid lg:grid-cols-2 gap-6">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <h3 className="text-lg font-bold text-white mb-3 flex items-start gap-2">
                  <FiInfo className="text-white mt-1 flex-shrink-0" size={18} />
                  {faq.question}
                </h3>
                <p className="text-gray-300 leading-relaxed">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Section */}
        <div className="bg-gray-900 rounded-2xl p-12 text-center border border-gray-700">
          <h2 className="text-4xl font-bold text-white mb-6">¿Listo para solicitar tu crédito?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Contáctanos hoy mismo y obtén la financiación que necesitas
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-gray-700 rounded-lg">
                  <FiPhone className="text-white" size={24} />
                </div>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Teléfono</h3>
              <p className="text-gray-300">+57 316 682 7239</p>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-gray-700 rounded-lg">
                  <FiMail className="text-white" size={24} />
                </div>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Email</h3>
              <p className="text-gray-300">creditos@geniusindustries.org</p>
            </div>
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-gray-700 rounded-lg">
                  <FiMapPin className="text-white" size={24} />
                </div>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Oficina Principal </h3>
              <p className="text-gray-300">Medellin, Colombia</p>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => setShowModal(true)}
              className="bg-white text-black font-semibold py-4 px-8 rounded-lg hover:bg-gray-200 transform hover:scale-105 transition-all duration-200 shadow-lg flex items-center gap-2"
            >
              <FiArrowUpRight size={20} />
              Solicitar Crédito Ahora
            </button>
            <button 
              onClick={() => document.getElementById('simulator')?.scrollIntoView({ behavior: 'smooth' })}
              className="border-2 border-white text-white font-semibold py-4 px-8 rounded-lg hover:bg-white hover:text-black transition-all duration-200"
            >
              Volver al Simulador
            </button>
          </div>
        </div>

        {/* Modal de Solicitud de Crédito */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-2xl p-8 border border-gray-700 max-w-md w-full max-h-[90vh] overflow-y-auto">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white mb-4">Solicitar Crédito</h2>
                <p className="text-gray-300">Elige cómo quieres proceder con tu solicitud</p>
              </div>

              {!showForm ? (
                <div className="space-y-4">
                  <button
                    onClick={() => {
                      window.open(whatsappUrl, '_blank');
                      setShowModal(false);
                    }}
                    className="w-full bg-green-600 text-white font-semibold py-4 px-6 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center justify-center gap-3"
                  >
                    <FiPhone size={20} />
                    Contactar por WhatsApp
                  </button>
                  <p className="text-gray-400 text-sm text-center">Te atenderemos inmediatamente</p>
                  
                  <div className="border-t border-gray-600 pt-4">
                    <button
                      onClick={() => setShowForm(true)}
                      className="w-full bg-white text-black font-semibold py-4 px-6 rounded-lg hover:bg-gray-200 transition-all duration-200 flex items-center justify-center gap-3"
                    >
                      <FiMail size={20} />
                      Llenar Formulario
                    </button>
                    <p className="text-gray-400 text-sm text-center mt-2">Enviaremos tu solicitud por correo y te contactaremos en 24-48 horas</p>
                  </div>
                  
                  <button
                    onClick={() => setShowModal(false)}
                    className="w-full mt-4 border border-gray-600 text-gray-300 font-semibold py-3 px-6 rounded-lg hover:bg-gray-800 transition-all duration-200"
                  >
                    Cancelar
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmitApplication} className="space-y-4">
                  <h3 className="text-lg font-bold text-white mb-4">Formulario de Solicitud</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Nombre Completo</label>
                      <input
                        type="text"
                        name="fullName"
                        value={formData.fullName}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Cédula/ID</label>
                      <input
                        type="text"
                        name="idNumber"
                        value={formData.idNumber}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Email</label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Teléfono WhatsApp</label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Tipo de Crédito</label>
                      <select
                        name="creditType"
                        value={formData.creditType}
                        onChange={handleInputChange}
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      >
                        <option value="personal">Personal</option>
                        <option value="business">Empresarial</option>
                        <option value="mortgage">Hipotecario</option>
                        <option value="vehicle">Vehículo</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Monto Solicitado</label>
                      <input
                        type="text"
                        name="requestedAmount"
                        value={formData.requestedAmount}
                        onChange={handleInputChange}
                        required
                        placeholder={selectedCountry.currency === 'EUR' ? '€10,000' : '$5,000,000 COP'}
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Ingresos Mensuales</label>
                      <input
                        type="text"
                        name="monthlyIncome"
                        value={formData.monthlyIncome}
                        onChange={handleInputChange}
                        required
                        placeholder={selectedCountry.currency === 'EUR' ? '€2,000' : '$2,000,000 COP'}
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Tipo de Empleo</label>
                      <select
                        name="employmentType"
                        value={formData.employmentType}
                        onChange={handleInputChange}
                        required
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      >
                        <option value="">Seleccionar</option>
                        <option value="empleado">Empleado</option>
                        <option value="independiente">Independiente</option>
                        <option value="empresario">Empresario</option>
                        <option value="pensionado">Pensionado</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-white font-semibold mb-1 text-sm">Propósito del Crédito</label>
                    <textarea
                      name="purpose"
                      value={formData.purpose}
                      onChange={handleInputChange}
                      required
                      rows={3}
                      className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                      placeholder="Describe para qué usarás el crédito..."
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="hasCollateral"
                      checked={formData.hasCollateral}
                      onChange={handleInputChange}
                      className="mr-2"
                    />
                    <label className="text-white text-sm">¿Tienes garantías o avales?</label>
                  </div>

                  {formData.hasCollateral && (
                    <div>
                      <label className="block text-white font-semibold mb-1 text-sm">Descripción de Garantías</label>
                      <textarea
                        name="collateralDescription"
                        value={formData.collateralDescription}
                        onChange={handleInputChange}
                        rows={2}
                        className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg p-2 text-sm focus:border-white focus:outline-none"
                        placeholder="Describe tus garantías o avales..."
                      />
                    </div>
                  )}

                  <div className="pt-4 space-y-3">
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-white text-black font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? 'Enviando...' : 'Enviar Solicitud'}
                    </button>
                    
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setShowForm(false)}
                        className="flex-1 border border-gray-600 text-gray-300 font-semibold py-2 px-4 rounded-lg hover:bg-gray-800 transition-all duration-200 text-sm"
                      >
                        Volver
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowForm(false);
                          setShowModal(false);
                        }}
                        className="flex-1 border border-gray-600 text-gray-300 font-semibold py-2 px-4 rounded-lg hover:bg-gray-800 transition-all duration-200 text-sm"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export const Route = createFileRoute('/credits')({
  component: CreditsPage,
});