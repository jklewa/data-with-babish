"""drop show, add tag and new episode columns

Revision ID: 8f2a1c4d9e30
Revises: 1fba43043f30
Create Date: 2026-05-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f2a1c4d9e30'
down_revision = '1fba43043f30'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('episode_show_id_fk', 'episode', type_='foreignkey')
    op.drop_constraint('episode_name_show_uindex', 'episode', type_='unique')
    op.drop_column('episode', 'show_id')
    op.drop_table('show')

    op.add_column('episode', sa.Column('slug', sa.String(), nullable=True))
    op.add_column('episode', sa.Column('time_to_cook', sa.Integer(), nullable=True))
    op.add_column('episode', sa.Column('yield_qty', sa.Integer(), nullable=True))
    op.add_column('episode', sa.Column('yield_unit', sa.String(), nullable=True))
    op.add_column('episode', sa.Column('video_views', sa.BigInteger(), nullable=True))

    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), server_default=sa.text("(nextval('tag_id_seq'::regclass))"), nullable=False),
        sa.Column('axis', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('axis', 'name', name='tag_axis_name_uindex'),
    )
    op.create_table(
        'episode_tags',
        sa.Column('episode_id', sa.String(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['episode_id'], ['episode.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id']),
        sa.PrimaryKeyConstraint('episode_id', 'tag_id'),
    )


def downgrade():
    op.drop_table('episode_tags')
    op.drop_table('tag')

    op.drop_column('episode', 'video_views')
    op.drop_column('episode', 'yield_unit')
    op.drop_column('episode', 'yield_qty')
    op.drop_column('episode', 'time_to_cook')
    op.drop_column('episode', 'slug')

    op.create_table(
        'show',
        sa.Column('id', sa.Integer(), server_default=sa.text("(nextval('show_id_seq'::regclass))"), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('image_link', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.add_column('episode', sa.Column('show_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('episode_name_show_uindex', 'episode', ['name', 'show_id'])
    op.create_foreign_key('episode_show_id_fk', 'episode', 'show', ['show_id'], ['id'])
