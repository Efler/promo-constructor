from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product


def list_products_for_seller(db: Session, seller_id: int) -> list[Product]:
    statement: Select[tuple[Product]] = (
        select(Product)
        .where(Product.seller_id == seller_id)
        .options(selectinload(Product.items))
        .order_by(Product.id)
    )
    return list(db.execute(statement).scalars().all())


def get_product_for_seller(db: Session, *, seller_id: int, product_id: int) -> Product | None:
    statement: Select[tuple[Product]] = (
        select(Product)
        .where(Product.seller_id == seller_id, Product.id == product_id)
        .options(selectinload(Product.items))
    )
    return db.execute(statement).scalar_one_or_none()


def get_product_by_vendor_code(db: Session, *, seller_id: int, vendor_code: str) -> Product | None:
    statement: Select[tuple[Product]] = select(Product).where(
        Product.seller_id == seller_id,
        Product.vendor_code == vendor_code,
    )
    return db.execute(statement).scalar_one_or_none()


def list_products_for_seller_by_ids(
    db: Session,
    *,
    seller_id: int,
    product_ids: list[int],
) -> list[Product]:
    if not product_ids:
        return []

    statement: Select[tuple[Product]] = (
        select(Product)
        .where(Product.seller_id == seller_id, Product.id.in_(product_ids))
        .order_by(Product.id)
    )
    return list(db.execute(statement).scalars().all())


def add_product(db: Session, product: Product) -> Product:
    db.add(product)
    return product
