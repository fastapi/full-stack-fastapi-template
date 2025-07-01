#!/usr/bin/env python3
"""
🚀 SCRIPT DE MIGRACIÓN COMPLETA PARA RAILWAY POSTGRESQL
Crea todas las tablas necesarias para GENIUS INDUSTRIES
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Optional
import asyncio

# Agregar el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from sqlalchemy import create_engine, text
    from sqlmodel import SQLModel
    import sqlalchemy as sa
except ImportError as e:
    print(f"❌ Error importing libraries: {e}")
    print("Install with: pip install psycopg2-binary sqlalchemy")
    sys.exit(1)

# CONFIGURACIÓN DE RAILWAY POSTGRESQL
RAILWAY_CONFIG = {
    "host": "postgres-production-bff4.up.railway.app",
    "port": 5432,
    "database": "railway",
    "user": "postgres",
    "password": "TU_PASSWORD_AQUI",  # ⚠️ CAMBIAR POR TU PASSWORD REAL
}

# SQL COMPLETO PARA CREAR TODAS LAS TABLAS
CREATE_TABLES_SQL = """
-- 🧹 LIMPIAR TABLAS EXISTENTES SI EXISTEN
DROP TABLE IF EXISTS generated_legal_documents CASCADE;
DROP TABLE IF EXISTS legal_document_templates CASCADE;
DROP TABLE IF EXISTS compliance_audit CASCADE;
DROP TABLE IF EXISTS data_protection_consent CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS property_visits CASCADE;
DROP TABLE IF EXISTS property_favorites CASCADE;
DROP TABLE IF EXISTS property_views CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS credits CASCADE;
DROP TABLE IF EXISTS mortgage_loans CASCADE;
DROP TABLE IF EXISTS investment_loans CASCADE;
DROP TABLE IF EXISTS market_analysis CASCADE;
DROP TABLE IF EXISTS agent_performance CASCADE;
DROP TABLE IF EXISTS financial_reports CASCADE;
DROP TABLE IF EXISTS dashboard_metrics CASCADE;
DROP TABLE IF EXISTS credit_scores CASCADE;
DROP TABLE IF EXISTS credit_history CASCADE;
DROP TABLE IF EXISTS risk_analysis CASCADE;

-- 🔧 EXTENSIONES NECESARIAS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 📊 TIPOS ENUM
CREATE TYPE user_role AS ENUM ('ceo', 'manager', 'supervisor', 'hr', 'support', 'agent', 'client', 'user');
CREATE TYPE property_type AS ENUM ('house', 'apartment', 'land', 'commercial', 'office');
CREATE TYPE property_status AS ENUM ('available', 'sold', 'rented', 'pending');
CREATE TYPE visit_status AS ENUM ('scheduled', 'completed', 'cancelled');
CREATE TYPE document_type AS ENUM ('sale_contract', 'rental_contract', 'loan_contract', 'intermediation_contract', 'privacy_policy', 'terms_conditions', 'mortgage_contract', 'promissory_note');
CREATE TYPE document_status AS ENUM ('draft', 'active', 'inactive', 'archived');
CREATE TYPE compliance_status AS ENUM ('compliant', 'non_compliant', 'pending_review');
CREATE TYPE loan_status AS ENUM ('pending', 'approved', 'rejected', 'active', 'completed', 'defaulted');

-- 👥 TABLA USUARIOS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📦 TABLA ITEMS (EJEMPLO)
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🏠 TABLA PROPIEDADES
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    property_type property_type NOT NULL,
    status property_status DEFAULT 'available',
    price DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20),
    bedrooms INTEGER,
    bathrooms INTEGER,
    area DECIMAL(10,2) NOT NULL,
    features JSONB DEFAULT '[]',
    amenities JSONB DEFAULT '[]',
    images JSONB DEFAULT '[]',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    year_built INTEGER,
    condition VARCHAR(50),
    parking_spaces INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0,
    visits INTEGER DEFAULT 0,
    agent_id UUID REFERENCES users(id),
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 👁️ TABLA VISTAS DE PROPIEDADES
CREATE TABLE property_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ❤️ TABLA FAVORITOS
CREATE TABLE property_favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id, user_id)
);

-- 🏠 TABLA VISITAS
CREATE TABLE property_visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    client_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES users(id) ON DELETE CASCADE,
    visit_date TIMESTAMP NOT NULL,
    status visit_status DEFAULT 'scheduled',
    notes TEXT,
    feedback JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 💰 TABLA TRANSACCIONES
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    buyer_id UUID REFERENCES users(id),
    seller_id UUID REFERENCES users(id),
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🏦 TABLA CRÉDITOS
CREATE TABLE credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    property_id UUID REFERENCES properties(id),
    amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,4) NOT NULL,
    term_months INTEGER NOT NULL,
    status loan_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🏡 TABLA PRÉSTAMOS HIPOTECARIOS
CREATE TABLE mortgage_loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id),
    user_id UUID REFERENCES users(id),
    loan_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,4) NOT NULL,
    term_years INTEGER NOT NULL,
    ltv_ratio DECIMAL(5,4) NOT NULL,
    monthly_payment DECIMAL(10,2) NOT NULL,
    insurance_required BOOLEAN DEFAULT false,
    insurance_provider VARCHAR(255),
    insurance_policy_number VARCHAR(255),
    insurance_coverage DECIMAL(15,2),
    appraisal_value DECIMAL(15,2) NOT NULL,
    appraisal_date TIMESTAMP NOT NULL,
    appraisal_company VARCHAR(255) NOT NULL,
    legal_documents JSONB DEFAULT '[]',
    status loan_status DEFAULT 'pending',
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approval_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 💼 TABLA PRÉSTAMOS DE INVERSIÓN
CREATE TABLE investment_loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID,
    user_id UUID REFERENCES users(id),
    loan_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,4) NOT NULL,
    term_years INTEGER NOT NULL,
    expected_roi DECIMAL(5,4),
    business_plan TEXT,
    collateral_type VARCHAR(100),
    collateral_value DECIMAL(15,2),
    collateral_documents JSONB DEFAULT '[]',
    risk_assessment JSONB,
    status loan_status DEFAULT 'pending',
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approval_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📊 TABLA ANÁLISIS DE MERCADO
CREATE TABLE market_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_type VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    period VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    metrics JSONB NOT NULL,
    insights JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📈 TABLA RENDIMIENTO AGENTES
CREATE TABLE agent_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES users(id),
    period VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    metrics JSONB NOT NULL,
    goals JSONB,
    achievements JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 💹 TABLA REPORTES FINANCIEROS
CREATE TABLE financial_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(50) NOT NULL,
    period VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    data JSONB NOT NULL,
    summary JSONB,
    analysis JSONB,
    recommendations JSONB DEFAULT '[]',
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📊 TABLA MÉTRICAS DASHBOARD
CREATE TABLE dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dashboard_type VARCHAR(50) NOT NULL,
    period VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    metrics JSONB NOT NULL,
    trends JSONB,
    alerts JSONB DEFAULT '[]',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🏦 TABLA PUNTAJES CREDITICIOS
CREATE TABLE credit_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES users(id),
    score INTEGER NOT NULL CHECK (score >= 300 AND score <= 850),
    factors JSONB,
    risk_level VARCHAR(20) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP NOT NULL,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 💳 TABLA HISTORIAL CREDITICIO
CREATE TABLE credit_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES users(id),
    loan_id UUID,
    payment_status VARCHAR(50) NOT NULL,
    delinquency_days INTEGER DEFAULT 0,
    payment_history JSONB DEFAULT '[]',
    credit_utilization DECIMAL(5,4),
    credit_limit DECIMAL(15,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ⚠️ TABLA ANÁLISIS DE RIESGOS
CREATE TABLE risk_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID,
    risk_score DECIMAL(5,4) NOT NULL,
    risk_factors JSONB,
    risk_level VARCHAR(20) NOT NULL,
    mitigation_measures JSONB DEFAULT '[]',
    monitoring_plan JSONB,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    last_reviewed TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📋 TABLA PLANTILLAS DOCUMENTOS LEGALES
CREATE TABLE legal_document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(255) NOT NULL,
    document_type document_type NOT NULL,
    version VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📄 TABLA DOCUMENTOS LEGALES GENERADOS
CREATE TABLE generated_legal_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES legal_document_templates(id),
    document_number VARCHAR(50) UNIQUE NOT NULL,
    document_type document_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    variables_used JSONB DEFAULT '{}',
    status document_status DEFAULT 'draft',
    client_id UUID REFERENCES users(id),
    property_id UUID REFERENCES properties(id),
    loan_id UUID,
    agent_id UUID REFERENCES users(id),
    generated_by UUID REFERENCES users(id),
    signed_by_client BOOLEAN DEFAULT false,
    signed_by_agent BOOLEAN DEFAULT false,
    signature_client_date TIMESTAMP,
    signature_agent_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🔍 TABLA AUDITORÍAS DE CUMPLIMIENTO
CREATE TABLE compliance_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    compliance_status compliance_status NOT NULL,
    findings JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    auditor_id UUID REFERENCES users(id),
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_audit_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🔒 TABLA CONSENTIMIENTOS PROTECCIÓN DE DATOS
CREATE TABLE data_protection_consent (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    consent_type VARCHAR(100) NOT NULL,
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consent_version VARCHAR(20) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    withdrawn_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📝 TABLA AUDITORÍA SISTEMA
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    changes JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🚀 ÍNDICES PARA PERFORMANCE
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_properties_type ON properties(property_type);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_city ON properties(city);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_property_views_property_id ON property_views(property_id);
CREATE INDEX idx_property_favorites_user_id ON property_favorites(user_id);
CREATE INDEX idx_property_visits_date ON property_visits(visit_date);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_credits_status ON credits(status);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- ⚡ TRIGGERS PARA UPDATED_AT
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_property_visits_updated_at BEFORE UPDATE ON property_visits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_credits_updated_at BEFORE UPDATE ON credits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mortgage_loans_updated_at BEFORE UPDATE ON mortgage_loans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investment_loans_updated_at BEFORE UPDATE ON investment_loans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 🎯 DATOS INICIALES
INSERT INTO users (email, hashed_password, full_name, role, is_superuser) VALUES
('admin@genius-industries.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrator', 'ceo', true),
('manager@genius-industries.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Manager', 'manager', false),
('agent@genius-industries.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Agent Demo', 'agent', false);

-- ✅ VERIFICACIÓN DE TABLAS CREADAS
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
"""

def create_connection_string(config):
    """Crear string de conexión a PostgreSQL."""
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def main():
    """Función principal para crear todas las tablas."""
    print("🚀 INICIANDO MIGRACIÓN COMPLETA A RAILWAY POSTGRESQL")
    print("=" * 60)
    
    # Verificar configuración
    if RAILWAY_CONFIG["password"] == "TU_PASSWORD_AQUI":
        print("❌ ERROR: Debes configurar tu password de Railway en el script")
        print("📝 Edita la variable RAILWAY_CONFIG['password'] con tu password real")
        return False
        
    connection_string = create_connection_string(RAILWAY_CONFIG)
    
    try:
        # Crear engine de SQLAlchemy
        print("🔌 Conectando a Railway PostgreSQL...")
        engine = create_engine(connection_string, echo=False)
        
        # Ejecutar todas las migraciones
        print("📊 Ejecutando migración completa...")
        with engine.connect() as connection:
            # Ejecutar en una sola transacción
            trans = connection.begin()
            try:
                # Ejecutar el SQL completo
                for statement in CREATE_TABLES_SQL.split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        connection.execute(text(statement))
                
                trans.commit()
                print("✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error en migración: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    print("\n📋 RESUMEN DE TABLAS CREADAS:")
    print("=" * 40)
    
    tables_created = [
        "✅ users (usuarios del sistema)",
        "✅ items (items de ejemplo)", 
        "✅ properties (propiedades inmobiliarias)",
        "✅ property_views (vistas de propiedades)",
        "✅ property_favorites (favoritos)",
        "✅ property_visits (visitas programadas)",
        "✅ transactions (transacciones)",
        "✅ credits (créditos)",
        "✅ mortgage_loans (préstamos hipotecarios)",
        "✅ investment_loans (préstamos de inversión)",
        "✅ market_analysis (análisis de mercado)",
        "✅ agent_performance (rendimiento agentes)",
        "✅ financial_reports (reportes financieros)",
        "✅ dashboard_metrics (métricas dashboard)",
        "✅ credit_scores (puntajes crediticios)",
        "✅ credit_history (historial crediticio)",
        "✅ risk_analysis (análisis de riesgos)",
        "✅ legal_document_templates (plantillas legales)",
        "✅ generated_legal_documents (documentos generados)",
        "✅ compliance_audit (auditorías)",
        "✅ data_protection_consent (consentimientos)",
        "✅ audit_log (log de auditoría)"
    ]
    
    for table in tables_created:
        print(f"  {table}")
    
    print("\n🎯 USUARIOS CREADOS:")
    print("  📧 admin@genius-industries.com (CEO)")
    print("  📧 manager@genius-industries.com (Manager)")  
    print("  📧 agent@genius-industries.com (Agent)")
    print("  🔑 Password: secret (cambiar en producción)")
    
    print("\n🚀 ¡TU BASE DE DATOS ESTÁ LISTA!")
    print("🔗 Puedes conectarte desde tu app usando las variables de entorno")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 MIGRACIÓN EXITOSA - Railway PostgreSQL listo para producción!")
    else:
        print("\n❌ MIGRACIÓN FALLÓ - Revisa los errores arriba")
        sys.exit(1) 