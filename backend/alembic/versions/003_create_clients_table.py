"""Create clients table

Revision ID: 003
Revises: 002
Create Date: 2026-01-29 15:25:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('client_type', sa.Enum('prospect', 'client', 'partner', name='clienttype'), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('siret', sa.String(), nullable=True),
        sa.Column('vat_number', sa.String(), nullable=True),
        sa.Column('contact_first_name', sa.String(), nullable=True),
        sa.Column('contact_last_name', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_phone', sa.String(), nullable=True),
        sa.Column('address_line1', sa.String(), nullable=True),
        sa.Column('address_line2', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=False, server_default='France'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('updated_at', sa.String(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_clients_company_name', 'clients', ['company_name'])
    op.create_index('ix_clients_email', 'clients', ['contact_email'])
    op.create_index('ix_clients_active', 'clients', ['is_active'])
    op.create_index('ix_clients_type', 'clients', ['client_type'])


def downgrade() -> None:
    op.drop_index('ix_clients_type', table_name='clients')
    op.drop_index('ix_clients_active', table_name='clients')
    op.drop_index('ix_clients_email', table_name='clients')
    op.drop_index('ix_clients_company_name', table_name='clients')
    op.drop_table('clients')
    op.execute('DROP TYPE clienttype')
