"""empty message

Revision ID: a1f1892aa3cc
Revises: 
Create Date: 2020-09-11 14:54:22.454035

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'a1f1892aa3cc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('controllers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mcuType', sqlalchemy_utils.types.choice.ChoiceType({'waterLevel': 'Water level', 'lightControl': 'Light control'}), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('macAddr', sa.Text(), nullable=True),
    sa.Column('isConfigured', sa.Boolean(), nullable=True),
    sa.Column('graph', sa.JSON(), nullable=True),
    sa.Column('esp_config', sa.JSON(), nullable=True),
    sa.Column('selfCheck', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('macAddr')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('controllers')
    # ### end Alembic commands ###
