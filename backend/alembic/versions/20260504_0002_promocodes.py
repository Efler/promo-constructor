"""add promocodes and promocode_products tables

Revision ID: 20260504_0002
Revises: 20260428_0001
Create Date: 2026-05-04 12:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260504_0002"
down_revision = "20260428_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "promocodes",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("seller_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("discount_mode", sa.String(length=16), nullable=False),
        sa.Column("discount_value", sa.Integer(), nullable=False),
        sa.Column("promo_type", sa.String(length=40), nullable=False),
        sa.Column("audience_type", sa.String(length=40), nullable=False),
        sa.Column("product_scope", sa.String(length=16), nullable=False),
        sa.Column("code", sa.String(length=15), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
            name="fk_promocodes_seller_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("code", name="uq_promocodes_code"),
        sa.CheckConstraint("length(btrim(title)) > 0", name="chk_promocodes_title_not_blank"),
        sa.CheckConstraint("ends_on >= starts_on", name="chk_promocodes_dates_order"),
        sa.CheckConstraint(
            "ends_on <= starts_on + 30",
            name="chk_promocodes_duration_max_31_days",
        ),
        sa.CheckConstraint(
            "discount_mode in ('percent', 'amount')",
            name="chk_promocodes_discount_mode",
        ),
        sa.CheckConstraint(
            "discount_value > 0",
            name="chk_promocodes_discount_value_positive",
        ),
        sa.CheckConstraint(
            "((discount_mode = 'percent' and discount_value between 1 and 99) "
            "or (discount_mode = 'amount' and discount_value >= 1))",
            name="chk_promocodes_discount_percent_range",
        ),
        sa.CheckConstraint(
            "promo_type in ('single_buyer_single_order', 'all_buyers_once', 'all_buyers_limited')",
            name="chk_promocodes_promo_type",
        ),
        sa.CheckConstraint(
            "audience_type in ('all', 'bought_last_half_year', 'not_bought_last_half_year')",
            name="chk_promocodes_audience_type",
        ),
        sa.CheckConstraint(
            "product_scope in ('all', 'selected')",
            name="chk_promocodes_product_scope",
        ),
        sa.CheckConstraint(
            "code ~ '^[A-Za-z0-9]{4,15}$'",
            name="chk_promocodes_code_format",
        ),
    )
    op.create_index("ix_promocodes_seller_id", "promocodes", ["seller_id"], unique=False)
    op.create_index("ix_promocodes_starts_on", "promocodes", ["starts_on"], unique=False)
    op.create_index("ix_promocodes_ends_on", "promocodes", ["ends_on"], unique=False)
    op.create_index("ix_promocodes_promo_type", "promocodes", ["promo_type"], unique=False)
    op.create_index("ix_promocodes_audience_type", "promocodes", ["audience_type"], unique=False)

    op.create_table(
        "promocode_products",
        sa.Column("promocode_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["promocode_id"],
            ["promocodes.id"],
            name="fk_promocode_products_promocode_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_promocode_products_product_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("promocode_id", "product_id", name="pk_promocode_products"),
    )
    op.create_index("ix_promocode_products_product_id", "promocode_products", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_promocode_products_product_id", table_name="promocode_products")
    op.drop_table("promocode_products")

    op.drop_index("ix_promocodes_audience_type", table_name="promocodes")
    op.drop_index("ix_promocodes_promo_type", table_name="promocodes")
    op.drop_index("ix_promocodes_ends_on", table_name="promocodes")
    op.drop_index("ix_promocodes_starts_on", table_name="promocodes")
    op.drop_index("ix_promocodes_seller_id", table_name="promocodes")
    op.drop_table("promocodes")
