"""Update relationships for categorias, subcategorias, and productos

Revision ID: bb3f0eb27408
Revises: 63e9ceea1e4d
Create Date: 2025-07-10 21:30:22.274178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb3f0eb27408'
down_revision = '63e9ceea1e4d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subcategoria_id', sa.Integer(), nullable=True))
        batch_op.alter_column('descripcion', existing_type=sa.TEXT(), type_=sa.String(length=255), existing_nullable=True)
        batch_op.alter_column('precio', existing_type=sa.NUMERIC(precision=10, scale=2), type_=sa.Float(), existing_nullable=False)
        batch_op.drop_column('categoria_id')
        batch_op.drop_column('fecha_creacion')
        batch_op.drop_column('estado')
    op.execute('UPDATE productos SET subcategoria_id = NULL WHERE subcategoria_id IS NULL')
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.alter_column('subcategoria_id', existing_type=sa.Integer(), nullable=True, existing_server_default=None)
        batch_op.create_foreign_key('fk_productos_subcategoria', 'subcategorias', ['subcategoria_id'], ['id'])

    # ### end Alembic commands ###

    # ### end Alembic commands ###

    # ### end Alembic commands ###

    # ### end Alembic commands ###

    # ### end Alembic commands ###

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('fk_productos_subcategoria', type_='foreignkey')
        batch_op.alter_column('subcategoria_id',
                             existing_type=sa.Integer(),
                             nullable=True,
                             existing_server_default=None)
        batch_op.add_column(sa.Column('estado', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('fecha_creacion', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('categoria_id', sa.Integer(), nullable=True))
        # Especificar un nombre para la clave foránea
        batch_op.create_foreign_key('fk_productos_categoria', 'categorias', ['categoria_id'], ['id'])
        batch_op.alter_column('precio',
                             existing_type=sa.Float(),
                             type_=sa.NUMERIC(precision=10, scale=2),
                             existing_nullable=False)
        batch_op.alter_column('descripcion',
                             existing_type=sa.String(length=255),
                             type_=sa.TEXT(),
                             existing_nullable=True)
        batch_op.drop_column('subcategoria_id')