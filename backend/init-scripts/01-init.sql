-- 🚀 GENIUS INDUSTRIES - POSTGRESQL INITIALIZATION SCRIPT
-- Este script se ejecuta automáticamente cuando se crea el contenedor PostgreSQL

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Crear esquemas adicionales si es necesario
-- CREATE SCHEMA IF NOT EXISTS audit;
-- CREATE SCHEMA IF NOT EXISTS reporting;

-- Mensaje de confirmación
SELECT 'GENIUS INDUSTRIES PostgreSQL Database initialized successfully!' AS status; 