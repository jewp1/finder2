"""update_matches_structure

Revision ID: ae0f5224df2d
Revises: 8e71b59af39d
Create Date: 2025-04-28 20:26:19.726519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae0f5224df2d'
down_revision = '8e71b59af39d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('matches', sa.Column('liked_user_id', sa.Integer(), nullable=False))
    op.drop_constraint('matches_project_id_fkey', 'matches', type_='foreignkey')
    op.create_foreign_key(None, 'matches', 'users', ['liked_user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('matches', 'project_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('matches', sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'matches', type_='foreignkey')
    op.create_foreign_key('matches_project_id_fkey', 'matches', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.drop_column('matches', 'liked_user_id')
    # ### end Alembic commands ### 