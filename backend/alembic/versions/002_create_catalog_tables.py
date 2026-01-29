"""Create catalog tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-29 15:15:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create materials table
    op.create_table(
        'materials',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name_fr', sa.String(), nullable=False),
        sa.Column('name_ro', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('price_eur', sa.Numeric(10, 2), nullable=False),
        sa.Column('price_lei', sa.Numeric(10, 2), nullable=True),
        sa.Column('price_date', sa.String(), nullable=False),
        sa.Column('supplier', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('updated_at', sa.String(), nullable=False),
    )
    op.create_index('ix_materials_code', 'materials', ['code'], unique=True)
    op.create_index('ix_materials_active', 'materials', ['is_active'])
    
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('material_cost', sa.Numeric(10, 2), nullable=False),
        sa.Column('labor_cost', sa.Numeric(10, 2), nullable=False),
        sa.Column('margin', sa.Numeric(5, 4), nullable=False, server_default='0.3'),
        sa.Column('overhead', sa.Numeric(5, 4), nullable=False, server_default='0.1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('updated_at', sa.String(), nullable=False),
    )
    op.create_index('ix_articles_code', 'articles', ['code'], unique=True)
    op.create_index('ix_articles_active', 'articles', ['is_active'])
    
    # Create article_materials junction table
    op.create_table(
        'article_materials',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('article_id', UUID(as_uuid=True), nullable=False),
        sa.Column('material_id', UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 4), nullable=False),
        sa.Column('waste_percent', sa.Numeric(5, 4), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id']),
    )
    op.create_index('ix_article_materials_article', 'article_materials', ['article_id'])
    
    # Create compositions table
    op.create_table(
        'compositions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('margin', sa.Numeric(5, 4), nullable=False, server_default='0.3'),
        sa.Column('overhead', sa.Numeric(5, 4), nullable=False, server_default='0.1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('updated_at', sa.String(), nullable=False),
    )
    op.create_index('ix_compositions_code', 'compositions', ['code'], unique=True)
    op.create_index('ix_compositions_active', 'compositions', ['is_active'])
    
    # Create composition_items table
    op.create_table(
        'composition_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('composition_id', UUID(as_uuid=True), nullable=False),
        sa.Column('item_type', sa.Enum('material', 'article', name='compositionitemtype'), nullable=False),
        sa.Column('item_id', UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 4), nullable=False),
        sa.ForeignKeyConstraint(['composition_id'], ['compositions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_composition_items_composition', 'composition_items', ['composition_id'])
    
    # Create services table
    op.create_table(
        'services',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('price_net', sa.Numeric(10, 2), nullable=False),
        sa.Column('price_gross', sa.Numeric(10, 2), nullable=False),
        sa.Column('margin', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.Column('updated_at', sa.String(), nullable=False),
    )
    op.create_index('ix_services_code', 'services', ['code'], unique=True)
    op.create_index('ix_services_active', 'services', ['is_active'])


def downgrade() -> None:
    op.drop_index('ix_services_active', table_name='services')
    op.drop_index('ix_services_code', table_name='services')
    op.drop_table('services')
    
    op.drop_index('ix_composition_items_composition', table_name='composition_items')
    op.drop_table('composition_items')
    op.execute('DROP TYPE compositionitemtype')
    
    op.drop_index('ix_compositions_active', table_name='compositions')
    op.drop_index('ix_compositions_code', table_name='compositions')
    op.drop_table('compositions')
    
    op.drop_index('ix_article_materials_article', table_name='article_materials')
    op.drop_table('article_materials')
    
    op.drop_index('ix_articles_active', table_name='articles')
    op.drop_index('ix_articles_code', table_name='articles')
    op.drop_table('articles')
    
    op.drop_index('ix_materials_active', table_name='materials')
    op.drop_index('ix_materials_code', table_name='materials')
    op.drop_table('materials')
