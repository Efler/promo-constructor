from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.promotion import Promotion
from app.models.promotion_participation import PromotionParticipation
from app.models.seller import Seller
from app.repositories.product import list_products_for_seller_by_ids
from app.repositories.promotion import (
    add_promotion_participation,
    get_participation_for_seller_and_promotion,
    get_published_promotion_by_slug,
    list_participations_for_seller,
    list_published_promotions,
    make_participation_product_link,
)
from app.schemas.promotion import (
    PromotionCatalogItem,
    PromotionParticipationCreate,
    PromotionParticipationRead,
    PromotionParticipationStatus,
    PromotionStatus,
)

_BUSINESS_TIMEZONE = ZoneInfo("Europe/Moscow")


def _current_business_datetime() -> datetime:
    return datetime.now(_BUSINESS_TIMEZONE)


def _current_business_date() -> date:
    return _current_business_datetime().date()


def _resolve_promotion_status(promotion: Promotion) -> PromotionStatus:
    today = _current_business_date()
    if promotion.ends_on < today:
        return "closed"
    if promotion.starts_on > today:
        return "upcoming"
    if (promotion.ends_on - today).days <= 3:
        return "ending_soon"
    return "active"


def _is_join_open(promotion: Promotion) -> bool:
    today = _current_business_date()
    return (
        promotion.is_published
        and today <= promotion.join_deadline
        and today <= promotion.ends_on
    )


def _resolve_participation_status(
    participation: PromotionParticipation,
) -> PromotionParticipationStatus:
    today = _current_business_date()
    promotion = participation.promotion
    if promotion.ends_on < today:
        return "completed"
    if promotion.starts_on > today:
        return "scheduled"
    return "active"


def _build_promotion_catalog_item(promotion: Promotion) -> PromotionCatalogItem:
    categories = sorted(promotion.categories, key=lambda category: category.parent_id)
    benefits = sorted(promotion.benefits, key=lambda benefit: benefit.position)
    return PromotionCatalogItem(
        id=promotion.id,
        slug=promotion.slug,
        title=promotion.title,
        short_description=promotion.short_description,
        starts_on=promotion.starts_on,
        ends_on=promotion.ends_on,
        join_deadline=promotion.join_deadline,
        minimum_discount_percent=promotion.minimum_discount_percent,
        minimum_stock_qty=promotion.minimum_stock_qty,
        minimum_products=promotion.minimum_products,
        category_scope=promotion.category_scope,
        eligible_parent_ids=[category.parent_id for category in categories],
        eligible_parent_names=(
            [category.parent_name for category in categories]
            if promotion.category_scope == "selected"
            else None
        ),
        benefits=[benefit.description for benefit in benefits],
        card_tone=promotion.card_tone,
        is_featured=promotion.is_featured,
        status=_resolve_promotion_status(promotion),
        join_open=_is_join_open(promotion),
    )


def _build_participation_read(
    participation: PromotionParticipation,
) -> PromotionParticipationRead:
    return PromotionParticipationRead(
        id=participation.id,
        promotion_id=participation.promotion_id,
        promotion_slug=participation.promotion.slug,
        promotion_title=participation.promotion.title,
        selected_product_ids=sorted(
            link.product_id for link in participation.product_links
        ),
        additional_discount_percent=participation.additional_discount_percent,
        joined_at=participation.joined_at,
        status=_resolve_participation_status(participation),
    )


def list_marketplace_promotions(db: Session) -> list[PromotionCatalogItem]:
    return [
        _build_promotion_catalog_item(promotion)
        for promotion in list_published_promotions(db)
    ]


def get_marketplace_promotion(
    db: Session,
    *,
    promotion_slug: str,
) -> PromotionCatalogItem:
    promotion = get_published_promotion_by_slug(db, promotion_slug)
    if promotion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found.",
        )
    return _build_promotion_catalog_item(promotion)


def list_seller_promotion_participations(
    db: Session,
    *,
    seller: Seller,
) -> list[PromotionParticipationRead]:
    return [
        _build_participation_read(participation)
        for participation in list_participations_for_seller(db, seller.id)
    ]


def _load_selected_products(
    db: Session,
    *,
    seller_id: int,
    product_ids: list[int],
) -> list[Product]:
    products = list_products_for_seller_by_ids(
        db,
        seller_id=seller_id,
        product_ids=product_ids,
    )
    if len(products) != len(product_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more selected products are unavailable for this seller.",
        )

    products_by_id = {product.id: product for product in products}
    return [products_by_id[product_id] for product_id in product_ids]


def _validate_selected_product(
    product: Product,
    *,
    promotion: Promotion,
    eligible_parent_ids: set[int],
) -> None:
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {product.id} is not active.",
        )

    active_items = [item for item in product.items if item.is_active]
    if not active_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {product.id} has no active items.",
        )

    active_stock = sum(item.stock_qty for item in active_items)
    if active_stock < promotion.minimum_stock_qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Product {product.id} stock is below the promotion minimum "
                f"of {promotion.minimum_stock_qty}."
            ),
        )

    if (
        promotion.category_scope == "selected"
        and product.parent_id not in eligible_parent_ids
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {product.id} category is not eligible for this promotion.",
        )


def create_seller_promotion_participation(
    db: Session,
    *,
    seller: Seller,
    promotion_slug: str,
    payload: PromotionParticipationCreate,
) -> PromotionParticipationRead:
    promotion = get_published_promotion_by_slug(
        db,
        promotion_slug,
        for_update=True,
    )
    if promotion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found.",
        )

    if not _is_join_open(promotion):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Promotion is not accepting new participations.",
        )

    if get_participation_for_seller_and_promotion(
        db,
        seller_id=seller.id,
        promotion_id=promotion.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seller already participates in this promotion.",
        )

    if payload.additional_discount_percent < promotion.minimum_discount_percent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Additional discount must be at least "
                f"{promotion.minimum_discount_percent}%."
            ),
        )

    if len(payload.selected_product_ids) < promotion.minimum_products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Promotion requires at least {promotion.minimum_products} products."
            ),
        )

    products = _load_selected_products(
        db,
        seller_id=seller.id,
        product_ids=payload.selected_product_ids,
    )
    eligible_parent_ids = {
        category.parent_id for category in promotion.categories
    }
    for product in products:
        _validate_selected_product(
            product,
            promotion=promotion,
            eligible_parent_ids=eligible_parent_ids,
        )

    confirmed_at = _current_business_datetime()
    participation = PromotionParticipation(
        promotion_id=promotion.id,
        seller_id=seller.id,
        additional_discount_percent=payload.additional_discount_percent,
        price_change_confirmed_at=confirmed_at,
        joined_at=confirmed_at,
        promotion=promotion,
        product_links=[
            make_participation_product_link(product.id) for product in products
        ],
    )
    add_promotion_participation(db, participation)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Promotion participation conflicts with an existing record.",
        ) from exc

    db.refresh(participation)
    return _build_participation_read(participation)
