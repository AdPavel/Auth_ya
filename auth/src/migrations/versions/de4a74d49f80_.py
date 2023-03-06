"""empty message

Revision ID: de4a74d49f80
Revises: 6dc84859d8c6
Create Date: 2023-03-06 14:23:05.112042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de4a74d49f80'
down_revision = '6dc84859d8c6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('social_account', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])


def downgrade():
    with op.batch_alter_table('log_history', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('user_device_type')

    # ### end Alembic commands ###
