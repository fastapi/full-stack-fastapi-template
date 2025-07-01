import React, { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { FiMenu, FiX } from 'react-icons/fi';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  const navigation = [
    { name: 'Inicio', href: '/' },
    { name: 'Nosotros', href: '/about' },
    { name: 'Inversiones', href: '/investment' },
    { name: 'Créditos', href: '/credits' },
    { name: 'Propiedades', href: '/marketplace' },
    { name: 'Contacto', href: '/contact' }
  ];

  return (
    <nav className="bg-black shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <img
                src="/assets/images/GENIUS-INDUSTRIES.png"
                alt="GENIUS INDUSTRIES"
                className="h-10 w-10 rounded-full object-cover"
              />
              <span className="text-white font-bold text-xl hidden sm:block">
                GENIUS INDUSTRIES
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="text-white hover:text-gray-300 px-3 py-2 text-sm font-medium transition-colors duration-200"
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              to="/sign-in"
              className="text-white hover:text-gray-300 px-3 py-2 text-sm font-medium transition-colors duration-200"
            >
              Iniciar Sesión
            </Link>
            <Link
              to="/sign-up"
              className="bg-white text-black hover:bg-gray-200 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            >
              Registrarse
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={toggleMenu}
              className="text-white hover:text-gray-300 focus:outline-none focus:text-gray-300"
            >
              {isMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-black border-t border-gray-800">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            <div className="pt-4 border-t border-gray-800">
              <Link
                to="/sign-in"
                className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Iniciar Sesión
              </Link>
              <Link
                to="/sign-up"
                className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Registrarse
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
