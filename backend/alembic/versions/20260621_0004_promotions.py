"""add marketplace promotions and seller participation tables

Revision ID: 20260621_0004
Revises: 20260615_0003
Create Date: 2026-06-21 18:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260621_0004"
down_revision = "20260615_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "promotions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("join_deadline", sa.Date(), nullable=False),
        sa.Column("minimum_discount_percent", sa.SmallInteger(), nullable=False),
        sa.Column(
            "minimum_stock_qty",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "minimum_products",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "category_scope",
            sa.String(length=16),
            nullable=False,
            server_default="all",
        ),
        sa.Column(
            "card_tone",
            sa.String(length=16),
            nullable=False,
            server_default="brand",
        ),
        sa.Column(
            "is_featured",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "is_published",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("slug", name="uq_promotions_slug"),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'",
            name="chk_promotions_slug_format",
        ),
        sa.CheckConstraint(
            "length(btrim(title)) > 0",
            name="chk_promotions_title_not_blank",
        ),
        sa.CheckConstraint(
            "length(btrim(short_description)) > 0",
            name="chk_promotions_description_not_blank",
        ),
        sa.CheckConstraint(
            "ends_on >= starts_on",
            name="chk_promotions_dates_order",
        ),
        sa.CheckConstraint(
            "join_deadline <= ends_on",
            name="chk_promotions_join_deadline",
        ),
        sa.CheckConstraint(
            "minimum_discount_percent between 1 and 99",
            name="chk_promotions_discount_range",
        ),
        sa.CheckConstraint(
            "minimum_stock_qty >= 0",
            name="chk_promotions_stock_non_negative",
        ),
        sa.CheckConstraint(
            "minimum_products >= 1",
            name="chk_promotions_minimum_products_positive",
        ),
        sa.CheckConstraint(
            "category_scope in ('all', 'selected')",
            name="chk_promotions_category_scope",
        ),
        sa.CheckConstraint(
            "card_tone in ('brand', 'teal', 'orange', 'blue', 'grape')",
            name="chk_promotions_card_tone",
        ),
    )
    op.create_index(
        "ix_promotions_catalog_period",
        "promotions",
        ["starts_on", "ends_on"],
        unique=False,
        postgresql_where=sa.text("is_published = true"),
    )
    op.create_index(
        "ix_promotions_join_deadline_published",
        "promotions",
        ["join_deadline"],
        unique=False,
        postgresql_where=sa.text("is_published = true"),
    )

    op.create_table(
        "promotion_benefits",
        sa.Column("promotion_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["promotion_id"],
            ["promotions.id"],
            name="fk_promotion_benefits_promotion_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "promotion_id",
            "position",
            name="pk_promotion_benefits",
        ),
        sa.CheckConstraint(
            "position between 1 and 2",
            name="chk_promotion_benefits_position",
        ),
        sa.CheckConstraint(
            "length(btrim(description)) > 0",
            name="chk_promotion_benefits_description_not_blank",
        ),
    )

    op.create_table(
        "promotion_categories",
        sa.Column("promotion_id", sa.BigInteger(), nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=False),
        sa.Column("parent_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["promotion_id"],
            ["promotions.id"],
            name="fk_promotion_categories_promotion_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "promotion_id",
            "parent_id",
            name="pk_promotion_categories",
        ),
        sa.CheckConstraint(
            "parent_id > 0",
            name="chk_promotion_categories_parent_id_positive",
        ),
        sa.CheckConstraint(
            "length(btrim(parent_name)) > 0",
            name="chk_promotion_categories_name_not_blank",
        ),
    )
    op.create_index(
        "ix_promotion_categories_parent_id",
        "promotion_categories",
        ["parent_id"],
        unique=False,
    )

    op.create_table(
        "promotion_participations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("promotion_id", sa.BigInteger(), nullable=False),
        sa.Column("seller_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "additional_discount_percent",
            sa.SmallInteger(),
            nullable=False,
        ),
        sa.Column(
            "price_change_confirmed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["promotion_id"],
            ["promotions.id"],
            name="fk_promotion_participations_promotion_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["sellers.id"],
            name="fk_promotion_participations_seller_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "seller_id",
            "promotion_id",
            name="uq_promotion_participations_seller_promotion",
        ),
        sa.CheckConstraint(
            "additional_discount_percent between 1 and 99",
            name="chk_promotion_participations_discount_range",
        ),
    )
    op.create_index(
        "ix_promotion_participations_promotion_id",
        "promotion_participations",
        ["promotion_id"],
        unique=False,
    )

    op.create_table(
        "promotion_participation_products",
        sa.Column("participation_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["participation_id"],
            ["promotion_participations.id"],
            name="fk_promotion_participation_products_participation_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_promotion_participation_products_product_id",
        ),
        sa.PrimaryKeyConstraint(
            "participation_id",
            "product_id",
            name="pk_promotion_participation_products",
        ),
    )
    op.create_index(
        "ix_promotion_participation_products_product_id",
        "promotion_participation_products",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_promotion_participation_products_product_id",
        table_name="promotion_participation_products",
    )
    op.drop_table("promotion_participation_products")

    op.drop_index(
        "ix_promotion_participations_promotion_id",
        table_name="promotion_participations",
    )
    op.drop_table("promotion_participations")

    op.drop_index(
        "ix_promotion_categories_parent_id",
        table_name="promotion_categories",
    )
    op.drop_table("promotion_categories")

    op.drop_table("promotion_benefits")

    op.drop_index(
        "ix_promotions_join_deadline_published",
        table_name="promotions",
        postgresql_where=sa.text("is_published = true"),
    )
    op.drop_index(
        "ix_promotions_catalog_period",
        table_name="promotions",
        postgresql_where=sa.text("is_published = true"),
    )
    op.drop_table("promotions")
