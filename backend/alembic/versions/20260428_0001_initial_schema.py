"""initial seller, product, and auth session schema

Revision ID: 20260428_0001
Revises: 
Create Date: 2026-04-28 13:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260428_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sellers",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("seller_sid", sa.Uuid(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("username", name="uq_sellers_username"),
        sa.UniqueConstraint("email", name="uq_sellers_email"),
        sa.UniqueConstraint("seller_sid", name="uq_sellers_seller_sid"),
    )
    op.create_index("ix_sellers_is_active", "sellers", ["is_active"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("seller_id", sa.BigInteger(), nullable=False),
        sa.Column("nm_id", sa.BigInteger(), nullable=True),
        sa.Column("imt_id", sa.BigInteger(), nullable=True),
        sa.Column("vendor_code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("subject_id", sa.BigInteger(), nullable=True),
        sa.Column("subject_name", sa.String(length=255), nullable=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("parent_name", sa.String(length=255), nullable=True),
        sa.Column("kiz_marked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("main_photo_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["seller_id"], ["sellers.id"], name="fk_products_seller_id", ondelete="CASCADE"),
        sa.UniqueConstraint("seller_id", "vendor_code", name="uq_products_seller_vendor_code"),
        sa.UniqueConstraint("nm_id", name="uq_products_nm_id"),
    )
    op.create_index("ix_products_seller_id", "products", ["seller_id"], unique=False)
    op.create_index("ix_products_subject_id", "products", ["subject_id"], unique=False)
    op.create_index("ix_products_parent_id", "products", ["parent_id"], unique=False)
    op.create_index("ix_products_is_active", "products", ["is_active"], unique=False)

    op.create_table(
        "product_items",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("size_id", sa.BigInteger(), nullable=True),
        sa.Column("tech_size_name", sa.String(length=100), nullable=False, server_default="ONE SIZE"),
        sa.Column("barcode", sa.String(length=64), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discounted_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("club_discounted_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="RUB"),
        sa.Column("discount_percent", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("club_discount_percent", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("editable_size_price", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_bad_turnover", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("stock_qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_product_items_product_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("product_id", "tech_size_name", name="uq_product_items_product_size_name"),
        sa.UniqueConstraint("product_id", "size_id", name="uq_product_items_product_size_id"),
        sa.UniqueConstraint("barcode", name="uq_product_items_barcode"),
        sa.CheckConstraint("price >= 0", name="chk_product_items_price_non_negative"),
        sa.CheckConstraint(
            "discounted_price is null or discounted_price >= 0",
            name="chk_product_items_discounted_price_non_negative",
        ),
        sa.CheckConstraint(
            "club_discounted_price is null or club_discounted_price >= 0",
            name="chk_product_items_club_discounted_price_non_negative",
        ),
        sa.CheckConstraint("stock_qty >= 0", name="chk_product_items_stock_qty_non_negative"),
        sa.CheckConstraint(
            "discount_percent between 0 and 100",
            name="chk_product_items_discount_percent_range",
        ),
        sa.CheckConstraint(
            "club_discount_percent between 0 and 100",
            name="chk_product_items_club_discount_percent_range",
        ),
    )
    op.create_index("ix_product_items_product_id", "product_items", ["product_id"], unique=False)
    op.create_index("ix_product_items_size_id", "product_items", ["size_id"], unique=False)
    op.create_index("ix_product_items_is_active", "product_items", ["is_active"], unique=False)

    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("seller_id", sa.BigInteger(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
            name="fk_refresh_sessions_seller_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_token_hash", name="uq_refresh_sessions_refresh_token_hash"),
        sa.CheckConstraint("expires_at >= created_at", name="chk_refresh_sessions_expires_after_created"),
    )
    op.create_index("ix_refresh_sessions_seller_id", "refresh_sessions", ["seller_id"], unique=False)
    op.create_index("ix_refresh_sessions_expires_at", "refresh_sessions", ["expires_at"], unique=False)
    op.create_index("ix_refresh_sessions_revoked_at", "refresh_sessions", ["revoked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_refresh_sessions_revoked_at", table_name="refresh_sessions")
    op.drop_index("ix_refresh_sessions_expires_at", table_name="refresh_sessions")
    op.drop_index("ix_refresh_sessions_seller_id", table_name="refresh_sessions")
    op.drop_table("refresh_sessions")

    op.drop_index("ix_product_items_is_active", table_name="product_items")
    op.drop_index("ix_product_items_size_id", table_name="product_items")
    op.drop_index("ix_product_items_product_id", table_name="product_items")
    op.drop_table("product_items")

    op.drop_index("ix_products_is_active", table_name="products")
    op.drop_index("ix_products_parent_id", table_name="products")
    op.drop_index("ix_products_subject_id", table_name="products")
    op.drop_index("ix_products_seller_id", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_sellers_is_active", table_name="sellers")
    op.drop_table("sellers")
