"""merge sale order and purchase order branches

Revision ID: cb1e8d33fb45
Revises: 1f66cda30a0a, 2ad1cf58c54f
Create Date: 2026-02-01 05:45:54.528309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb1e8d33fb45'
down_revision = ('1f66cda30a0a', '2ad1cf58c54f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
