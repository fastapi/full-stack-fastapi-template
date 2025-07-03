/**
 * Utilidad para verificar y debuggear variables de entorno
 * GENIUS INDUSTRIES - Frontend Environment Checker
 */

interface EnvConfig {
  VITE_CLERK_PUBLISHABLE_KEY: string
  VITE_API_URL: string
  VITE_ENVIRONMENT: string
  VITE_PROJECT_NAME: string
  VITE_FRONTEND_HOST: string
  VITE_DEBUG: string
}

/**
 * Verifica que todas las variables de entorno requeridas estén disponibles
 */
export function checkEnvironmentVariables(): EnvConfig {
  const env = import.meta.env

  // Variables requeridas
  const requiredVars = [
    'VITE_CLERK_PUBLISHABLE_KEY',
    'VITE_API_URL',
  ] as const

  // Variables opcionales con valores por defecto
  const optionalVars = {
    VITE_ENVIRONMENT: 'local',
    VITE_PROJECT_NAME: 'Genius Industries',
    VITE_FRONTEND_HOST: 'http://localhost:5173',
    VITE_DEBUG: 'false',
  } as const

  // Verificar variables requeridas
  const missing: string[] = []
  for (const varName of requiredVars) {
    if (!env[varName]) {
      missing.push(varName)
    }
  }

  if (missing.length > 0) {
    console.error('❌ Variables de entorno faltantes:', missing)
    throw new Error(`Variables de entorno requeridas faltantes: ${missing.join(', ')}`)
  }

  // Construir configuración final
  const config: EnvConfig = {
    VITE_CLERK_PUBLISHABLE_KEY: env.VITE_CLERK_PUBLISHABLE_KEY,
    VITE_API_URL: env.VITE_API_URL,
    VITE_ENVIRONMENT: env.VITE_ENVIRONMENT || optionalVars.VITE_ENVIRONMENT,
    VITE_PROJECT_NAME: env.VITE_PROJECT_NAME || optionalVars.VITE_PROJECT_NAME,
    VITE_FRONTEND_HOST: env.VITE_FRONTEND_HOST || optionalVars.VITE_FRONTEND_HOST,
    VITE_DEBUG: env.VITE_DEBUG || optionalVars.VITE_DEBUG,
  }

  // Debug en desarrollo
  if (config.VITE_DEBUG === 'true' && import.meta.env.DEV) {
    console.group('🔧 Configuración de Variables de Entorno')
    console.log('Environment:', config.VITE_ENVIRONMENT)
    console.log('Project:', config.VITE_PROJECT_NAME)
    console.log('API URL:', config.VITE_API_URL)
    console.log('Frontend Host:', config.VITE_FRONTEND_HOST)
    console.log('Clerk Key:', config.VITE_CLERK_PUBLISHABLE_KEY ? '✅ Configurada' : '❌ Faltante')
    console.log('Debug Mode:', config.VITE_DEBUG)
    console.groupEnd()
  }

  return config
}

/**
 * Obtiene la configuración verificada de variables de entorno
 */
export const envConfig = checkEnvironmentVariables() 