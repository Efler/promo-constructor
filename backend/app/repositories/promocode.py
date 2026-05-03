from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.promocode import Promocode


def add_promocode(db: Session, promocode: Promocode) -> Promocode:
    db.add(promocode)
    return promocode


def get_promocode_by_code(db: Session, code: str) -> Promocode | None:
    statement: Select[tuple[Promocode]] = (
        select(Promocode)
        .where(Promocode.code == code)
        .options(selectinload(Promocode.product_links))
    )
    return db.execute(statement).scalar_one_or_none()


def list_promocodes_for_seller(db: Session, seller_id: int) -> list[Promocode]:
    statement: Select[tuple[Promocode]] = (
        select(Promocode)
        .where(Promocode.seller_id == seller_id)
        .options(selectinload(Promocode.product_links))
        .order_by(Promocode.created_at.desc(), Promocode.id.desc())
    )
    return list(db.execute(statement).scalars().all())
