"""Create company table

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-03-23 18:20:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "company",
        sa.Column("cnpj", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("razao_social", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("data_abertura", sa.Date(), nullable=False),
        sa.Column("nome_fantasia", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("porte", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("atividade_economica_principal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("atividade_economica_secundaria", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("natureza_juridica", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("logradouro", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("numero", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("complemento", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("cep", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("bairro", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("municipio", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("uf", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False),
        sa.Column("endereco_eletronico", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("telefone_comercial", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("situacao_cadastral", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("data_situacao_cadastral", sa.Date(), nullable=False),
        sa.Column("cpf_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=14), nullable=False),
        sa.Column("identidade_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("logradouro_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("numero_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("complemento_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("cep_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("bairro_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("municipio_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("uf_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=False),
        sa.Column("endereco_eletronico_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("telefones_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("data_nascimento_representante_legal", sa.Date(), nullable=False),
        sa.Column("banco_cc_cnpj", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("agencia_cc_cnpj", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_company_cnpj"), "company", ["cnpj"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_company_cnpj"), table_name="company")
    op.drop_table("company")
