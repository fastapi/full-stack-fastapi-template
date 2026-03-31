"""Initial schema for SQL Server

Revision ID: 0001
Revises:
Create Date: 2026-03-30 21:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table(
        "user",
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column(
            "role",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="comercial",
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)

    # Create item table
    op.create_table(
        "item",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create company table
    op.create_table(
        "company",
        sa.Column("cnpj", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("razao_social", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("data_abertura", sa.Date(), nullable=True),
        sa.Column("nome_fantasia", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("porte", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("atividade_economica_principal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("atividade_economica_secundaria", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("natureza_juridica", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("logradouro", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("numero", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("complemento", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("cep", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True),
        sa.Column("bairro", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("municipio", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("uf", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=True),
        sa.Column("endereco_eletronico", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("telefone_comercial", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("situacao_cadastral", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("data_situacao_cadastral", sa.Date(), nullable=True),
        sa.Column("cpf_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=14), nullable=True),
        sa.Column("identidade_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("logradouro_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("numero_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("complemento_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("cep_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True),
        sa.Column("bairro_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("municipio_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("uf_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=True),
        sa.Column("endereco_eletronico_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("telefones_representante_legal", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=True),
        sa.Column("data_nascimento_representante_legal", sa.Date(), nullable=True),
        sa.Column("banco_cc_cnpj", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("agencia_cc_cnpj", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="completed",
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_company_cnpj"), "company", ["cnpj"], unique=True)

    # Create companyinvite table
    op.create_table(
        "companyinvite",
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("token", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companyinvite_token"), "companyinvite", ["token"], unique=True)

    # Create auditlog table
    op.create_table(
        "auditlog",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "action",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("target_user_id", sa.Uuid(), nullable=False),
        sa.Column("performed_by_id", sa.Uuid(), nullable=False),
        sa.Column(
            "changes",
            sqlmodel.sql.sqltypes.AutoString(length=2000),
            nullable=False,
            server_default="",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["target_user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["performed_by_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("auditlog")
    op.drop_index(op.f("ix_companyinvite_token"), table_name="companyinvite")
    op.drop_table("companyinvite")
    op.drop_index(op.f("ix_company_cnpj"), table_name="company")
    op.drop_table("company")
    op.drop_table("item")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
