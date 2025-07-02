import React, { useEffect } from 'react';
import { FaFacebook, FaTwitter, FaInstagram, FaLinkedin, FaPhone, FaEnvelope, FaMapMarkerAlt } from 'react-icons/fa';

// Declaración de tipos para window.chatwootSDK
declare global {
  interface Window {
    chatwootSDK?: any;
    chatwootSettings?: any;
  }
}

// Tipos para los links del footer
interface FooterLink {
  name: string;
  href: string;
  icon?: React.ReactElement;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

const Footer: React.FC = () => {
  useEffect(() => {
    // Configurar Chatwoot
    const initChatwoot = () => {
      // Evitar duplicar el script
      if (window.chatwootSDK) {
        return;
      }

      // Configuración de Chatwoot
      window.chatwootSettings = {
        hideMessageBubble: false,
        position: 'right',
        locale: 'es',
        type: 'standard',
      };

      // Cargar script de Chatwoot
      const script = document.createElement('script');
      script.src = 'https://chat-geniusindustries.up.railway.app/packs/js/sdk.js';
      script.defer = true;
      script.async = true;
      
      script.onload = () => {
        if (window.chatwootSDK) {
          window.chatwootSDK.run({
            websiteToken: 'D6zXewaMkYtWBpKL1fSjpCtb',
            baseUrl: 'https://chat-geniusindustries.up.railway.app'
          });
        }
      };

      document.head.appendChild(script);
    };

    initChatwoot();

    // Cleanup
    return () => {
      if (window.chatwootSDK) {
        // Cleanup si es necesario
      }
    };
  }, []);

  const footerLinks: FooterSection[] = [
    {
      title: 'Empresa',
      links: [
        { name: 'Acerca de', href: '/about' },
        { name: 'Contacto', href: '/contact' },
        { name: 'Marketplace', href: '/marketplace' },
        { name: 'Inversiones', href: '/investment' },
      ]
    },
    {
      title: 'Servicios',
      links: [
        { name: 'Compra de Propiedades', href: '/marketplace' },
        { name: 'Créditos Inmobiliarios', href: '/credits' },
        { name: 'Inversiones', href: '/investment' },
        { name: 'Asesoría Legal', href: '/contact' },
      ]
    },
    {
      title: 'Contacto',
      links: [
        { name: '+57 300 123 4567', href: 'tel:+573001234567', icon: <FaPhone /> },
        { name: 'info@geniusindustries.org', href: 'mailto:info@geniusindustries.org', icon: <FaEnvelope /> },
        { name: 'Bogotá, Colombia', href: '#', icon: <FaMapMarkerAlt /> },
      ]
    }
  ];

  return (
    <footer className="bg-black text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <span className="text-black font-bold text-sm">GI</span>
              </div>
              <span className="text-xl font-bold">GENIUS INDUSTRIES</span>
            </div>
            <p className="text-gray-300 mb-6">
              Líder en el mercado inmobiliario y financiero, ofreciendo soluciones integrales 
              para la compra, venta y financiación de propiedades.
            </p>
            <div className="flex space-x-4">
              <a href="https://facebook.com" className="text-gray-400 hover:text-white transition-colors">
                <FaFacebook size={20} />
              </a>
              <a href="https://twitter.com" className="text-gray-400 hover:text-white transition-colors">
                <FaTwitter size={20} />
              </a>
              <a href="https://instagram.com" className="text-gray-400 hover:text-white transition-colors">
                <FaInstagram size={20} />
              </a>
              <a href="https://linkedin.com" className="text-gray-400 hover:text-white transition-colors">
                <FaLinkedin size={20} />
              </a>
            </div>
          </div>

          {/* Footer Links */}
          {footerLinks.map((section, index) => (
            <div key={index}>
              <h3 className="font-semibold text-lg mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <a 
                      href={link.href}
                      className="text-gray-300 hover:text-white transition-colors flex items-center space-x-2"
                    >
                      {link.icon && <span>{link.icon}</span>}
                      <span>{link.name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © {new Date().getFullYear()} GENIUS INDUSTRIES. Todos los derechos reservados.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="/privacy" className="text-gray-400 hover:text-white text-sm transition-colors">
              Política de Privacidad
            </a>
            <a href="/terms" className="text-gray-400 hover:text-white text-sm transition-colors">
              Términos de Servicio
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 