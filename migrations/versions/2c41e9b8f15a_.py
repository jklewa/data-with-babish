"""drop episode.video_views

Revision ID: 2c41e9b8f15a
Revises: 8f2a1c4d9e30
Create Date: 2026-05-04 23:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c41e9b8f15a'
down_revision = '8f2a1c4d9e30'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('episode', 'video_views')


def downgrade():
    op.add_column('episode', sa.Column('video_views', sa.BigInteger(), nullable=True))
