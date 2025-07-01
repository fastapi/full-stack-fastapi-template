import React, { useState } from "react";
import { createFileRoute } from '@tanstack/react-router';
import { FiSearch, FiHome, FiTrendingUp, FiUsers, FiBriefcase, FiChevronLeft, FiChevronRight, FiStar } from "react-icons/fi";

const featuredProperties = [
  {
    img: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80",
    title: "Casa Moderna en Bogotá",
    price: "$350,000 USD",
    location: "Bogotá, Colombia",
    desc: "4 habitaciones · 3 baños · 250m²"
  },
  {
    img: "https://images.unsplash.com/photo-1460518451285-97b6aa326961?auto=format&fit=crop&w=600&q=80",
    title: "Penthouse de Lujo",
    price: "$1,200,000 USD",
    location: "Medellín, Colombia",
    desc: "5 habitaciones · 5 baños · 500m²"
  },
  {
    img: "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=600&q=80",
    title: "Apartamento Ejecutivo",
    price: "$220,000 USD",
    location: "Cali, Colombia",
    desc: "2 habitaciones · 2 baños · 120m²"
  },
];

const services = [
  { icon: <FiHome className="text-white" size={32} />, title: "Marketplace Inmobiliario", desc: "Compra, vende o arrienda propiedades en las principales ciudades." },
  { icon: <FiTrendingUp className="text-white" size={32} />, title: "Gestión de Activos", desc: "Administración profesional de portafolios inmobiliarios y financieros." },
  { icon: <FiBriefcase className="text-white" size={32} />, title: "Inversiones Seguras", desc: "Oportunidades de inversión con altos retornos y bajo riesgo." },
  { icon: <FiUsers className="text-white" size={32} />, title: "Asesoría Personalizada", desc: "Expertos que te acompañan en cada paso del proceso." },
];

const alliances = [
  { name: "Bancolombia", logo: "https://upload.wikimedia.org/wikipedia/commons/7/7a/Bancolombia_logo.svg" },
  { name: "Davivienda", logo: "https://upload.wikimedia.org/wikipedia/commons/2/2a/Logo_Davivienda.svg" },
  { name: "Grupo Sura", logo: "https://upload.wikimedia.org/wikipedia/commons/2/2d/Grupo_Sura_logo.svg" },
  { name: "Visa", logo: "https://upload.wikimedia.org/wikipedia/commons/4/41/Visa_Logo.png" },
];

const testimonials = [
  { name: "Juan Pérez", text: "GENIUS me ayudó a encontrar la casa de mis sueños. ¡Excelente servicio!", rating: 5 },
  { name: "María López", text: "Invertí y obtuve grandes retornos. El equipo es muy profesional.", rating: 5 },
  { name: "Carlos Ruiz", text: "La gestión de activos es impecable. Recomiendo GENIUS a todos mis colegas.", rating: 4 },
];

function HomePage() {
  const [propertyIndex, setPropertyIndex] = useState(0);
  const nextProperty = () => setPropertyIndex((i) => (i + 1) % featuredProperties.length);
  const prevProperty = () => setPropertyIndex((i) => (i - 1 + featuredProperties.length) % featuredProperties.length);

  return (
    <div className="w-full">
      {/* Hero + Buscador */}
      <section className="relative bg-black text-white py-24 px-4 flex flex-col items-center justify-center">
        <h1 className="text-5xl md:text-6xl font-extrabold mb-4 text-center drop-shadow-lg text-white">
          Soluciones Inmobiliarias & Gestión de Activos
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-8 text-center max-w-2xl">
          Liderando el mercado de bienes raíces e inversiones en Latinoamérica. Encuentra tu propiedad ideal o gestiona tu portafolio con expertos.
        </p>
        
        {/* Buscador */}
        <form className="flex flex-col md:flex-row gap-4 w-full max-w-2xl bg-gray-800 bg-opacity-90 rounded-xl p-4 shadow-lg">
          <div className="flex-1 flex items-center bg-gray-700 rounded-lg px-3">
            <FiSearch className="text-gray-400 mr-2" size={22} />
            <input 
              type="text" 
              placeholder="Buscar ciudad, zona o código..." 
              className="bg-transparent outline-none text-white w-full py-2 placeholder-gray-400" 
            />
          </div>
          <button 
            type="submit" 
            className="bg-white text-black hover:bg-gray-200 transition-colors font-bold rounded-lg px-8 py-2 shadow-md"
          >
            Buscar
          </button>
        </form>
      </section>

      {/* Carusel de propiedades */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Propiedades Destacadas</h2>
          <div className="relative flex items-center justify-center">
            <button 
              onClick={prevProperty} 
              className="absolute left-0 z-10 bg-gray-700 hover:bg-gray-600 rounded-full p-2 shadow transition-colors"
            >
              <FiChevronLeft size={28} className="text-white" />
            </button>
            
            <div className="flex flex-col md:flex-row items-center gap-8 w-full justify-center">
              <img 
                src={featuredProperties[propertyIndex].img} 
                alt="Propiedad" 
                className="rounded-2xl w-80 h-56 object-cover shadow-xl border-4 border-gray-700" 
              />
              <div className="text-white max-w-xs">
                <h3 className="text-2xl font-bold mb-2">{featuredProperties[propertyIndex].title}</h3>
                <div className="text-white font-bold text-lg mb-1">{featuredProperties[propertyIndex].price}</div>
                <div className="text-gray-300 mb-1">{featuredProperties[propertyIndex].location}</div>
                <div className="text-gray-400 mb-4">{featuredProperties[propertyIndex].desc}</div>
                <button className="bg-white text-black hover:bg-gray-200 transition-colors px-6 py-2 rounded-lg font-bold shadow">
                  Ver Detalles
                </button>
              </div>
            </div>
            
            <button 
              onClick={nextProperty} 
              className="absolute right-0 z-10 bg-gray-700 hover:bg-gray-600 rounded-full p-2 shadow transition-colors"
            >
              <FiChevronRight size={28} className="text-white" />
            </button>
          </div>
        </div>
      </section>

      {/* Servicios */}
      <section className="py-16 bg-black">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white mb-10 text-center">Nuestros Servicios</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {services.map((s) => (
              <div 
                key={s.title} 
                className="bg-gray-800 rounded-2xl p-8 flex flex-col items-center shadow-lg hover:scale-105 transition-transform border border-gray-700"
              >
                {s.icon}
                <div className="font-bold text-lg text-white mt-4 mb-2 text-center">{s.title}</div>
                <div className="text-gray-400 text-center">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Alianzas */}
      <section className="py-12 bg-gray-900">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Alianzas Estratégicas</h2>
          <div className="flex flex-wrap justify-center items-center gap-10">
            {alliances.map((a) => (
              <div 
                key={a.name} 
                className="bg-white rounded-xl p-4 flex items-center shadow-md hover:shadow-lg transition-shadow" 
                style={{ minWidth: 120, minHeight: 60 }}
              >
                <img src={a.logo} alt={a.name} className="h-10 object-contain mx-auto" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonios */}
      <section className="py-16 bg-black">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white mb-8 text-center">Testimonios</h2>
          <div className="flex flex-col md:flex-row gap-8 justify-center items-stretch">
            {testimonials.map((t) => (
              <div 
                key={t.name} 
                className="bg-gray-800 rounded-2xl p-8 flex-1 shadow-lg hover:scale-105 transition-transform border border-gray-700"
              >
                <div className="flex gap-1 mb-2">
                  {[...Array(t.rating)].map((_, i) => <FiStar key={i} className="text-white" />)}
                </div>
                <div className="text-white font-bold mb-2">{t.name}</div>
                <div className="text-gray-400 italic">"{t.text}"</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="py-16 bg-gray-900 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">¿Listo para invertir o encontrar tu propiedad?</h2>
        <p className="text-lg mb-8">Únete a la comunidad líder en gestión inmobiliaria y de activos en Latinoamérica.</p>
        <a 
          href="/marketplace" 
          className="bg-white text-black font-bold px-10 py-4 rounded-xl shadow-lg hover:bg-gray-200 transition-colors inline-block"
        >
          Explorar Marketplace
        </a>
      </section>
    </div>
  );
}

export const Route = createFileRoute('/')({
  component: HomePage,
});  
