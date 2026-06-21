from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.promotion import Promotion
from app.models.promotion_participation import PromotionParticipation
from app.models.promotion_participation_product import PromotionParticipationProduct


def list_published_promotions(db: Session) -> list[Promotion]:
    statement: Select[tuple[Promotion]] = (
        select(Promotion)
        .where(Promotion.is_published.is_(True))
        .options(
            selectinload(Promotion.benefits),
            selectinload(Promotion.categories),
        )
        .order_by(Promotion.starts_on, Promotion.id)
    )
    return list(db.execute(statement).scalars().all())


def get_published_promotion_by_slug(
    db: Session,
    slug: str,
    *,
    for_update: bool = False,
) -> Promotion | None:
    statement: Select[tuple[Promotion]] = (
        select(Promotion)
        .where(Promotion.slug == slug, Promotion.is_published.is_(True))
        .options(
            selectinload(Promotion.benefits),
            selectinload(Promotion.categories),
        )
    )
    if for_update:
        statement = statement.with_for_update()
    return db.execute(statement).scalar_one_or_none()


def list_participations_for_seller(
    db: Session,
    seller_id: int,
) -> list[PromotionParticipation]:
    statement: Select[tuple[PromotionParticipation]] = (
        select(PromotionParticipation)
        .where(PromotionParticipation.seller_id == seller_id)
        .options(
            selectinload(PromotionParticipation.promotion),
            selectinload(PromotionParticipation.product_links),
        )
        .order_by(
            PromotionParticipation.joined_at.desc(),
            PromotionParticipation.id.desc(),
        )
    )
    return list(db.execute(statement).scalars().all())


def get_participation_for_seller_and_promotion(
    db: Session,
    *,
    seller_id: int,
    promotion_id: int,
) -> PromotionParticipation | None:
    statement: Select[tuple[PromotionParticipation]] = (
        select(PromotionParticipation)
        .where(
            PromotionParticipation.seller_id == seller_id,
            PromotionParticipation.promotion_id == promotion_id,
        )
        .options(
            selectinload(PromotionParticipation.promotion),
            selectinload(PromotionParticipation.product_links),
        )
    )
    return db.execute(statement).scalar_one_or_none()


def add_promotion_participation(
    db: Session,
    participation: PromotionParticipation,
) -> PromotionParticipation:
    db.add(participation)
    return participation


def make_participation_product_link(product_id: int) -> PromotionParticipationProduct:
    return PromotionParticipationProduct(product_id=product_id)
