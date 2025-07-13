"""add_training_models

Revision ID: add_training_models
Revises: add_ai_soul_entity_models
Create Date: 2024-03-24 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'add_training_models'
down_revision: Union[str, None] = 'add_ai_soul_entity_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create TrainingMessage table
    op.create_table(
        'trainingmessage',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('content', sa.String(length=5000), nullable=False),
        sa.Column('is_from_trainer', sa.Boolean(), nullable=False),
        sa.Column('ai_soul_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('embedding', sa.String(length=10000), nullable=True),
        sa.ForeignKeyConstraint(['ai_soul_id'], ['aisoulentity.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create TrainingDocument table
    op.create_table(
        'trainingdocument',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('ai_soul_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('upload_timestamp', sa.DateTime(), nullable=False),
        sa.Column('processing_status', sa.String(length=50), nullable=False),
        sa.Column('chunk_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ai_soul_id'], ['aisoulentity.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create TrainingDocumentChunk table
    op.create_table(
        'trainingdocumentchunk',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('training_document_id', postgresql.UUID(), nullable=False),
        sa.Column('ai_soul_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('content', sa.String(length=2000), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_metadata', sa.String(length=1000), nullable=True),
        sa.Column('embedding', sa.String(length=10000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['training_document_id'], ['trainingdocument.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ai_soul_id'], ['aisoulentity.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('trainingdocumentchunk')
    op.drop_table('trainingdocument')
    op.drop_table('trainingmessage') 