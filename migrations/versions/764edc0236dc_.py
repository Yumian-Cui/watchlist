"""empty message

Revision ID: 764edc0236dc
Revises: 68afc4d4ce66
Create Date: 2024-01-31 13:20:02.555716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '764edc0236dc'
down_revision = '68afc4d4ce66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('email_confirmed', sa.Boolean(), nullable=True))
        batch_op.create_unique_constraint("uq_username", ['username'])
        batch_op.create_unique_constraint("uq_email", ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('email_confirmed')
        batch_op.drop_column('email')

    # ### end Alembic commands ###