"""agregar relacion subcategorias a categoria

Revision ID: b80a19a4188f
Revises: bb3f0eb27408
Create Date: 2025-07-26 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b80a19a4188f'
down_revision = 'bb3f0eb27408'
branch_labels = None
depends_on = None

def upgrade():
    # No se necesitan cambios adicionales ya que subcategoria_id ya existe y tiene datos válidos
    pass

def downgrade():
    # No se necesitan cambios reversibles significativos
    pass