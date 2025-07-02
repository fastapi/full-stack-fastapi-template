// 🌐 Configuración del Cliente API - GENIUS INDUSTRIES
// Configuración automática según entorno

import { OpenAPI } from './core/OpenAPI';

// Función para detectar el entorno y configurar la URL base
function configureApiClient(): void {
  // Detectar si estamos en producción por el dominio o variable de entorno
  const isProduction = 
    window.location.hostname === 'geniusindustries.org' ||
    window.location.hostname === 'www.geniusindustries.org' ||
    import.meta.env.VITE_ENV === 'production' ||
    import.meta.env.NODE_ENV === 'production';

  // Configurar URL base según el entorno
  if (isProduction) {
    // Producción: usar api.geniusindustries.org
    OpenAPI.BASE = 'https://api.geniusindustries.org';
  } else {
    // Desarrollo: usar localhost
    OpenAPI.BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }

  // Configuración adicional
  OpenAPI.CREDENTIALS = 'include';
  OpenAPI.WITH_CREDENTIALS = true;

  // Headers por defecto
  OpenAPI.HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  console.log(`🌐 Cliente API configurado para: ${OpenAPI.BASE}`);
}

// Configurar automáticamente al importar
configureApiClient();

export { configureApiClient };
export { OpenAPI } from './core/OpenAPI';

// Re-exportar todo lo necesario del cliente
export * from './sdk.gen';
export * from './types.gen';
export { ApiError } from './core/ApiError';
export { CancelablePromise, CancelError } from './core/CancelablePromise'; 