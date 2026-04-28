from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.seller import Seller


def get_seller_by_id(db: Session, seller_id: int) -> Seller | None:
    return db.get(Seller, seller_id)


def get_seller_by_username(db: Session, username: str) -> Seller | None:
    statement: Select[tuple[Seller]] = select(Seller).where(Seller.username == username)
    return db.execute(statement).scalar_one_or_none()


def get_seller_by_email(db: Session, email: str) -> Seller | None:
    statement: Select[tuple[Seller]] = select(Seller).where(Seller.email == email)
    return db.execute(statement).scalar_one_or_none()


def add_seller(db: Session, seller: Seller) -> Seller:
    db.add(seller)
    return seller
