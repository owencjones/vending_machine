"""create structure

Revision ID: 968e2513bee9
Revises: 
Create Date: 2024-01-28 20:57:14.631403

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "968e2513bee9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("username", sa.String, nullable=False, unique=True, index=True),
        sa.Column("deposit", sa.Integer, nullable=True),
        sa.Column("role", sa.Enum("SELLER", "BUYER"), nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("disabled", sa.Boolean, nullable=False),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("amount_available", sa.Integer, nullable=False),
        sa.Column("cost", sa.Integer, nullable=False),
        sa.Column("product_name", sa.String, nullable=False),
        sa.Column("seller_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("user_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expiry_time", sa.DateTime, nullable=False),
        sa.Column("deposited_amount", sa.Integer, nullable=False),
    )

    op.create_table(
        "session_products",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column(
            "session_id", sa.String, sa.ForeignKey("sessions.id"), nullable=False
        ),
        sa.Column(
            "product_id", sa.String, sa.ForeignKey("products.id"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("session_products")
    op.drop_table("user_sessions")
    op.drop_table("products")
    op.drop_table("users")
