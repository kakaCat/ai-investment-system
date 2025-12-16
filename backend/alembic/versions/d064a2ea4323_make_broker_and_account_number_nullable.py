"""make_broker_and_account_number_nullable

Revision ID: d064a2ea4323
Revises: 1f2bce260ec4
Create Date: 2025-12-10 00:00:02.613188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd064a2ea4323'
down_revision = '1f2bce260ec4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 修改 broker 列为可空
    op.alter_column('accounts', 'broker',
               existing_type=sa.String(length=100),
               nullable=True)

    # 修改 account_number 列为可空
    op.alter_column('accounts', 'account_number',
               existing_type=sa.String(length=50),
               nullable=True)


def downgrade() -> None:
    # 回滚：改回非空（需要先处理NULL值）
    op.execute("UPDATE accounts SET broker = '未知' WHERE broker IS NULL")
    op.execute("UPDATE accounts SET account_number = '-' WHERE account_number IS NULL")

    op.alter_column('accounts', 'broker',
               existing_type=sa.String(length=100),
               nullable=False)

    op.alter_column('accounts', 'account_number',
               existing_type=sa.String(length=50),
               nullable=False)
