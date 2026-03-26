"""Add company invite table and update company fields

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-26 16:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6g7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to company table
    op.add_column(
        "company",
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    )
    op.add_column(
        "company",
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="completed",
        ),
    )

    # Make company fields nullable to support partial initial creation
    columns_to_make_nullable = [
        "razao_social", "representante_legal", "nome_fantasia", "porte",
        "atividade_economica_principal", "atividade_economica_secundaria",
        "natureza_juridica", "logradouro", "numero", "complemento", "cep",
        "bairro", "municipio", "uf", "endereco_eletronico", "telefone_comercial",
        "situacao_cadastral", "cpf_representante_legal",
        "identidade_representante_legal", "logradouro_representante_legal",
        "numero_representante_legal", "complemento_representante_legal",
        "cep_representante_legal", "bairro_representante_legal",
        "municipio_representante_legal", "uf_representante_legal",
        "endereco_eletronico_representante_legal", "telefones_representante_legal",
        "banco_cc_cnpj", "agencia_cc_cnpj",
    ]
    date_columns_to_make_nullable = [
        "data_abertura", "data_situacao_cadastral", "data_nascimento_representante_legal",
    ]

    for col_name in columns_to_make_nullable:
        op.alter_column("company", col_name, existing_type=sa.String(), nullable=True)

    for col_name in date_columns_to_make_nullable:
        op.alter_column("company", col_name, existing_type=sa.Date(), nullable=True)

    # Create companyinvite table
    op.create_table(
        "companyinvite",
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("token", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companyinvite_token"), "companyinvite", ["token"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_companyinvite_token"), table_name="companyinvite")
    op.drop_table("companyinvite")

    # Revert company columns to non-nullable
    columns_to_make_non_nullable = [
        "razao_social", "representante_legal", "nome_fantasia", "porte",
        "atividade_economica_principal", "atividade_economica_secundaria",
        "natureza_juridica", "logradouro", "numero", "complemento", "cep",
        "bairro", "municipio", "uf", "endereco_eletronico", "telefone_comercial",
        "situacao_cadastral", "cpf_representante_legal",
        "identidade_representante_legal", "logradouro_representante_legal",
        "numero_representante_legal", "complemento_representante_legal",
        "cep_representante_legal", "bairro_representante_legal",
        "municipio_representante_legal", "uf_representante_legal",
        "endereco_eletronico_representante_legal", "telefones_representante_legal",
        "banco_cc_cnpj", "agencia_cc_cnpj",
    ]
    date_columns_to_make_non_nullable = [
        "data_abertura", "data_situacao_cadastral", "data_nascimento_representante_legal",
    ]

    for col_name in columns_to_make_non_nullable:
        op.alter_column("company", col_name, existing_type=sa.String(), nullable=False)

    for col_name in date_columns_to_make_non_nullable:
        op.alter_column("company", col_name, existing_type=sa.Date(), nullable=False)

    op.drop_column("company", "status")
    op.drop_column("company", "email")
