"""convert episode name to be unique by show

Revision ID: 1fba43043f30
Revises: c68d372abaa7
Create Date: 2021-02-22 21:53:44.025720

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '1fba43043f30'
down_revision = 'c68d372abaa7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('episode_name_show_uindex', 'episode', ['name', 'show_id'])
    op.drop_constraint('episode_name_key', 'episode', type_='unique')


def downgrade():
    op.create_unique_constraint('episode_name_key', 'episode', ['name'])
    op.drop_constraint('episode_name_show_uindex', 'episode', type_='unique')
