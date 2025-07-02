import React, { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { FiMenu, FiX, FiUser, FiLogOut, FiHome, FiUsers, FiTrendingUp, FiDollarSign, FiMail, FiMapPin } from 'react-icons/fi';
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

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, isLoaded } = useUser();
  const { signOut } = useAuth();

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  const navigation = [
    { name: 'Inicio', href: '/', icon: FiHome },
    { name: 'Nosotros', href: '/about', icon: FiUsers },
    { name: 'Inversiones', href: '/investment', icon: FiTrendingUp },
    { name: 'Créditos', href: '/credits', icon: FiDollarSign },
    { name: 'Propiedades', href: '/marketplace', icon: FiMapPin },
    { name: 'Contacto', href: '/contact', icon: FiMail }
  ];

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/';
  };

  const getDashboardUrl = () => {
    if (!user) return '/client-dashboard';
    const userRole = user.publicMetadata?.role as string;
    return getRedirectUrlByRole(userRole);
  };

  const getUserDisplayName = () => {
    if (!user) return '';
    return user.firstName || user.emailAddresses[0]?.emailAddress || 'Usuario';
  };

  // Mientras carga, mostrar un navbar básico
  if (!isLoaded) {
    return (
      <nav className="bg-black shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-3">
                <img
                  src="/assets/images/GENIUS-INDUSTRIES.png"
                  alt="GENIUS INDUSTRIES"
                  className="h-10 w-10 rounded-full object-cover"
                />
                
              </Link>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              {navigation.map((item) => {
                const IconComponent = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-white hover:text-gray-300 px-3 py-2 text-sm font-medium transition-colors duration-200 flex items-center gap-2"
                  >
                    <IconComponent size={16} />
                    {item.name}
                  </Link>
                );
              })}
            </div>

            <div className="hidden md:flex items-center space-x-4">
              <div className="w-20 h-8 bg-gray-700 animate-pulse rounded"></div>
            </div>
          </div>
        </div>
      </nav>
    );
  }

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
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => {
              const IconComponent = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-white hover:text-gray-300 px-3 py-2 text-sm font-medium transition-colors duration-200 flex items-center gap-2 hover:scale-105 transform transition-transform"
                >
                  <IconComponent size={16} />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Auth Buttons - Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              // Usuario autenticado
              <>
                <span className="text-gray-300 text-sm hidden lg:block">
                  Hola, {getUserDisplayName()}
                </span>
                <Link
                  to={getDashboardUrl()}
                  className="text-white hover:text-gray-300 px-3 py-2 text-sm font-medium transition-colors duration-200 flex items-center gap-2 hover:scale-105 transform transition-transform"
                >
                  <FiUser size={16} />
                  Dashboard
                </Link>
                <button
                  onClick={handleSignOut}
                  className="bg-white text-black hover:bg-gray-200 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center gap-2 hover:scale-105 transform transition-transform"
                >
                  <FiLogOut size={16} />
                  Cerrar Sesión
                </button>
              </>
            ) : (
              // Usuario no autenticado
              <>
                <Link
                  to="/sign-in"
                  className="text-white hover:text-gray-300 px-3 py-2 text-sm font-medium transition-colors duration-200 flex items-center gap-2 hover:scale-105 transform transition-transform"
                >
                  <FiUser size={16} />
                  Iniciar Sesión
                </Link>
                <Link
                  to="/sign-up"
                  className="bg-white text-black hover:bg-gray-200 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 relative group flex items-center gap-2 hover:scale-105 transform transition-transform"
                  title="Registro disponible solo para clientes"
                >
                  <FiUsers size={16} />
                  Registrarse
                  <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    Solo clientes
                  </span>
                </Link>
              </>
            )}
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
            {navigation.map((item) => {
              const IconComponent = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md flex items-center gap-3"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <IconComponent size={18} />
                  {item.name}
                </Link>
              );
            })}
            
            {/* Mobile Auth Section */}
            <div className="pt-4 border-t border-gray-800 space-y-2">
              {user ? (
                // Usuario autenticado - Mobile
                <>
                  <div className="px-3 py-2 text-gray-300 text-sm">
                    Hola, {getUserDisplayName()}
                  </div>
                  <Link
                    to={getDashboardUrl()}
                    className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md flex items-center gap-3"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <FiUser size={18} />
                    Dashboard
                  </Link>
                  <button
                    onClick={() => {
                      handleSignOut();
                      setIsMenuOpen(false);
                    }}
                    className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md flex items-center gap-3 w-full text-left"
                  >
                    <FiLogOut size={18} />
                    Cerrar Sesión
                  </button>
                </>
              ) : (
                // Usuario no autenticado - Mobile
                <>
                  <Link
                    to="/sign-in"
                    className="text-white hover:bg-gray-800 block px-3 py-2 text-base font-medium rounded-md flex items-center gap-3"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <FiUser size={18} />
                    Iniciar Sesión
                  </Link>
                  <div className="px-3 py-1">
                    <Link
                      to="/sign-up"
                      className="bg-white text-black hover:bg-gray-200 block px-3 py-2 text-base font-medium rounded-md text-center transition-colors duration-200 flex items-center justify-center gap-2"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      <FiUsers size={18} />
                      Registrarse (Solo Clientes)
                    </Link>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
