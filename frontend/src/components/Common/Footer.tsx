import React, { useEffect } from 'react';
import { Link } from '@tanstack/react-router';
import { FiFacebook, FiInstagram, FiLinkedin, FiMail, FiPhone } from 'react-icons/fi';
import { FaTiktok, FaWhatsapp } from 'react-icons/fa';

// Declaración de tipos para Chatwoot
declare global {
  interface Window {
    chatwootSDK?: {
      run: (config: { websiteToken: string; baseUrl: string }) => void;
    };
  }
}

const Footer = () => {
  const socialLinks = [
    { name: 'Facebook', icon: FiFacebook, href: 'https://www.facebook.com/geniusindustries1' },
    { name: 'Tiktok', icon: FaTiktok, href: 'https://www.tiktok.com/@geniusindustriesl' },
    { name: 'Instagram', icon: FiInstagram, href: 'https://www.instagram.com/geniu_industries_int' },
    { name: 'LinkedIn', icon: FiLinkedin, href: 'https://www.linkedin.com/company/genius-industries-international/' },
    { name: 'Whatsapp', icon: FaWhatsapp, href: 'https://whatsapp.com/channel/0029Vacz5n0CHDyglZc7a11X' },
  ];

  const quickLinks = [
    { name: 'Nosotros', href: '/about' },
    { name: 'Propiedades', href: '/marketplace' },
    { name: 'Inversiones', href: '/investment' },
    { name: 'Contacto', href: '/contact' }
  ];

  const legalLinks = [
    { name: 'Políticas de Privacidad', href: '#' },
    { name: 'Términos de Uso', href: '#' },
    { name: 'Cookies', href: '#' }
  ];

  // Efecto para cargar el script de Chatwoot
  useEffect(() => {
    // Configuración de Chatwoot
    const BASE_URL = "https://chat-geniusindustries.up.railway.app";
    const websiteToken = 'D6zXewaMkYtWBpKL1fSjpCtb';

    // Función para cargar Chatwoot
    const loadChatwoot = () => {
      // Verificar si ya existe el script
      if (document.querySelector(`script[src="${BASE_URL}/packs/js/sdk.js"]`)) {
        return;
      }

      // Crear y configurar el script
      const script = document.createElement('script');
      script.src = `${BASE_URL}/packs/js/sdk.js`;
      script.defer = true;
      script.async = true;

      // Función onload del script
      script.onload = function() {
        if (window.chatwootSDK) {
          window.chatwootSDK.run({
            websiteToken: websiteToken,
            baseUrl: BASE_URL
          });
        }
      };

      // Agregar el script al DOM
      document.head.appendChild(script);
    };

    // Cargar Chatwoot
    loadChatwoot();

    // Cleanup function (opcional)
    return () => {
      // Si necesitas limpiar el script al desmontar el componente
      const existingScript = document.querySelector(`script[src="${BASE_URL}/packs/js/sdk.js"]`);
      if (existingScript) {
        existingScript.remove();
      }
    };
  }, []); // Array vacío significa que se ejecuta solo una vez al montar

  return (
    <footer className="bg-black text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <img
                src="/assets/images/GENIUS-INDUSTRIES.png"
                alt="GENIUS INDUSTRIES"
                className="h-10 w-10 rounded-full object-cover"
              />
              <span className="text-xl font-bold">GENIUS INDUSTRIES</span>
            </div>
            <p className="text-gray-400 mb-6 max-w-md">
              Lideramos el mercado de bienes raíces e inversiones en Latinoamérica, 
              ofreciendo soluciones inmobiliarias y gestión de activos de clase mundial.
            </p>
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-gray-400">
                <FiMail className="w-4 h-4" />
                <span>info@geniusindustries.org</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-400">
                <FiPhone className="w-4 h-4" />
                <span>+57 (316) 682 7239</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Enlaces Rápidos</h3>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-gray-400 hover:text-white transition-colors duration-200"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Social Media */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Síguenos</h3>
            <div className="flex space-x-4">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.name}
                    href={social.href}
                    className="text-gray-400 hover:text-white transition-colors duration-200"
                    aria-label={social.name}
                  >
                    <Icon className="w-6 h-6" />
                  </a>
                );
              })}
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2019 GENIUS INDUSTRIES. Todos los derechos reservados.
            </p>
            <div className="flex space-x-6">
              {legalLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  className="text-gray-400 hover:text-white text-sm transition-colors duration-200"
                >
                  {link.name}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 