import React from "react";
import { createFileRoute } from '@tanstack/react-router';
import { FiMail, FiPhone, FiMapPin, FiSend } from "react-icons/fi";

function ContactPage() {
  return (
    <div className="bg-gray-900 min-h-screen py-16 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16 ">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            Contáctanos
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            ¿Tienes preguntas sobre nuestros servicios inmobiliarios? Estamos aquí para ayudarte. 
            Completa el formulario o usa nuestros datos de contacto directo.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <div className="bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-700 ">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <FiSend className="text-white" />
              Envíanos un mensaje
            </h2>
            
            <form className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Nombre completo
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Tu nombre"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="tu@email.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Teléfono
                </label>
                <input
                  type="tel"
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="+57 300 123 4567"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Asunto
                </label>
                <select className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                  <option>Consulta general</option>
                  <option>Compra de propiedad</option>
                  <option>Venta de propiedad</option>
                  <option>Inversión inmobiliaria</option>
                  <option>Gestión de activos</option>
                  <option>Asesoría legal</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Mensaje
                </label>
                <textarea
                  rows={5}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                  placeholder="Describe tu consulta o necesidad..."
                />
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-4 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Enviar mensaje
              </button>
            </form>
          </div>

          {/* Contact Info */}
          <div className="space-y-8 ">
            {/* Direct Contact */}
            <div className="bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-700">
              <h2 className="text-2xl font-bold text-white mb-6">Información de contacto</h2>
              
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="bg-gray-600 p-3 rounded-lg">
                    <FiMail className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Email</h3>
                    <p className="text-gray-300">info@geniusindustries.org</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-green-600 p-3 rounded-lg">
                    <FiPhone className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Teléfono</h3>
                    <p className="text-gray-300">+57 (316) 682 7239</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-purple-600 p-3 rounded-lg">
                    <FiMapPin className="text-white text-xl" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Ubicación</h3>
                    <p className="text-gray-300">
                      Medellin, Colombia
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Office Hours */}
            <div className="bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-700">
              <h2 className="text-2xl font-bold text-white mb-6">Horarios de atención</h2>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-gray-300">Lunes - Viernes</span>
                  <span className="text-white font-medium">8:00 AM - 5:30 PM</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-gray-300">Sábados</span>
                  <span className="text-white font-medium">9:00 AM - 2:00 PM</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-300">Domingos</span>
                  <span className="text-red-400 font-medium">Cerrado</span>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold text-white mb-4">¿Necesitas atención inmediata?</h3>
              <p className="text-blue-100 mb-6">
                Nuestro equipo está disponible para consultas urgentes
              </p>
              <a
                href="tel:+573166827239"
                className="inline-flex items-center gap-2 bg-white text-blue-600 font-semibold py-3 px-6 rounded-lg hover:bg-blue-50 transition-colors"
              >
                <FiPhone />
                Llamar ahora
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute('/contact')({
  component: ContactPage,
}); 
