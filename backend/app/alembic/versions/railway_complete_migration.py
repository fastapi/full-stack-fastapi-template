"""Railway complete migration

Revision ID: railway_complete_migration
Revises: 
Create Date: 2024-12-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'railway_complete_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Crear esquema completo para Railway PostgreSQL"""
    
    # Crear extensiones
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")
    
    # Crear tipos ENUM
    user_role_enum = postgresql.ENUM(
        'ceo', 'manager', 'supervisor', 'hr', 'support', 'agent', 'client', 'user',
        name='user_role'
    )
    user_role_enum.create(op.get_bind())
    
    property_type_enum = postgresql.ENUM(
        'house', 'apartment', 'land', 'commercial', 'office',
        name='property_type'
    )
    property_type_enum.create(op.get_bind())
    
    property_status_enum = postgresql.ENUM(
        'available', 'sold', 'rented', 'pending',
        name='property_status'
    )
    property_status_enum.create(op.get_bind())
    
    visit_status_enum = postgresql.ENUM(
        'scheduled', 'completed', 'cancelled',
        name='visit_status'
    )
    visit_status_enum.create(op.get_bind())
    
    document_type_enum = postgresql.ENUM(
        'sale_contract', 'rental_contract', 'loan_contract', 'intermediation_contract',
        'privacy_policy', 'terms_conditions', 'mortgage_contract', 'promissory_note',
        name='document_type'
    )
    document_type_enum.create(op.get_bind())
    
    document_status_enum = postgresql.ENUM(
        'draft', 'active', 'inactive', 'archived',
        name='document_status'
    )
    document_status_enum.create(op.get_bind())
    
    compliance_status_enum = postgresql.ENUM(
        'compliant', 'non_compliant', 'pending_review',
        name='compliance_status'
    )
    compliance_status_enum.create(op.get_bind())
    
    loan_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'active', 'completed', 'defaulted',
        name='loan_status'
    )
    loan_status_enum.create(op.get_bind())
    
    # Tabla users
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('role', user_role_enum, nullable=False, default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Tabla items
    op.create_table('items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabla properties
    op.create_table('properties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('property_type', property_type_enum, nullable=False),
        sa.Column('status', property_status_enum, nullable=False, default='available'),
        sa.Column('price', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False, default='USD'),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('state', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('country', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('zip_code', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('bathrooms', sa.Integer(), nullable=True),
        sa.Column('area', sa.Numeric(10, 2), nullable=False),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='[]'),
        sa.Column('amenities', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='[]'),
        sa.Column('images', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='[]'),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('year_built', sa.Integer(), nullable=True),
        sa.Column('condition', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('parking_spaces', sa.Integer(), nullable=False, default=0),
        sa.Column('views', sa.Integer(), nullable=False, default=0),
        sa.Column('favorites', sa.Integer(), nullable=False, default=0),
        sa.Column('visits', sa.Integer(), nullable=False, default=0),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_properties_type', 'properties', ['property_type'])
    op.create_index('idx_properties_status', 'properties', ['status'])
    op.create_index('idx_properties_city', 'properties', ['city'])
    op.create_index('idx_properties_price', 'properties', ['price'])
    
    # Tabla property_views
    op.create_table('property_views',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_property_views_property_id', 'property_views', ['property_id'])
    
    # Tabla property_favorites
    op.create_table('property_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('property_id', 'user_id')
    )
    op.create_index('idx_property_favorites_user_id', 'property_favorites', ['user_id'])
    
    # Tabla property_visits
    op.create_table('property_visits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visit_date', sa.DateTime(), nullable=False),
        sa.Column('status', visit_status_enum, nullable=False, default='scheduled'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('feedback', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_property_visits_date', 'property_visits', ['visit_date'])
    
    # Tabla audit_log
    op.create_table('audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('entity_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='{}'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='{}'),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('idx_audit_log_entity', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_log_created_at', 'audit_log', ['created_at'])
    
    # Crear función para updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Crear triggers para updated_at
    op.execute("CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_property_visits_updated_at BEFORE UPDATE ON property_visits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    
    # Insertar datos iniciales
    op.execute("""
        INSERT INTO users (email, hashed_password, full_name, role, is_superuser) VALUES
        ('admin@genius-industries.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrator', 'ceo', true),
        ('manager@genius-industries.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Manager', 'manager', false),
        ('agent@genius-industries.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Agent Demo', 'agent', false);
    """)


def downgrade():
    """Eliminar todo el esquema"""
    # Eliminar triggers
    op.execute("DROP TRIGGER IF EXISTS update_property_visits_updated_at ON property_visits;")
    op.execute("DROP TRIGGER IF EXISTS update_properties_updated_at ON properties;")
    op.execute("DROP TRIGGER IF EXISTS update_items_updated_at ON items;")
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users;")
    
    # Eliminar función
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Eliminar tablas
    op.drop_table('audit_log')
    op.drop_table('property_visits')
    op.drop_table('property_favorites')
    op.drop_table('property_views')
    op.drop_table('properties')
    op.drop_table('items')
    op.drop_table('users')
    
    # Eliminar tipos enum
    op.execute("DROP TYPE IF EXISTS loan_status;")
    op.execute("DROP TYPE IF EXISTS compliance_status;")
    op.execute("DROP TYPE IF EXISTS document_status;")
    op.execute("DROP TYPE IF EXISTS document_type;")
    op.execute("DROP TYPE IF EXISTS visit_status;")
    op.execute("DROP TYPE IF EXISTS property_status;")
    op.execute("DROP TYPE IF EXISTS property_type;")
    op.execute("DROP TYPE IF EXISTS user_role;")
    
    # Eliminar extensiones
    op.execute("DROP EXTENSION IF EXISTS \"pgcrypto\";")
    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\";") 