from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from secrets import choice
from string import ascii_uppercase, digits
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.promocode import Promocode
from app.models.promocode_product import PromocodeProduct
from app.models.seller import Seller
from app.repositories.product import list_products_for_seller_by_ids
from app.repositories.promocode import add_promocode, get_promocode_by_code, list_promocodes_for_seller
from app.schemas.promocode import PromocodeCreate, PromocodeListItem, PromocodeRead, PromocodeStatus

_PROMOCODE_ALPHABET = ascii_uppercase + digits
_BUSINESS_TIMEZONE = ZoneInfo("Europe/Moscow")


def _current_business_date() -> date:
    return datetime.now(_BUSINESS_TIMEZONE).date()


def _add_calendar_months(base_date: date, months: int) -> date:
    month_index = base_date.month - 1 + months
    year = base_date.year + month_index // 12
    month = month_index % 12 + 1

    day = min(base_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def normalize_promocode_code(code: str) -> str:
    return code.strip().upper()


def _resolve_promocode_status(promocode: Promocode) -> PromocodeStatus:
    return "expired" if promocode.ends_on < _current_business_date() else "active"


def validate_promocode_dates(payload: PromocodeCreate) -> None:
    today = _current_business_date()
    tomorrow = date.fromordinal(today.toordinal() + 1)
    latest_start = _add_calendar_months(today, 3)

    if payload.starts_on < tomorrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promocode start date must not be earlier than the next day.",
        )

    if payload.starts_on > latest_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promocode start date must not be later than 3 months from today.",
        )


def is_promocode_code_available(db: Session, code: str) -> bool:
    normalized_code = normalize_promocode_code(code)
    if not normalized_code:
        return False
    return get_promocode_by_code(db, normalized_code) is None


def _generate_unique_promocode_code(db: Session) -> str:
    for _ in range(20):
        generated = "".join(choice(_PROMOCODE_ALPHABET) for _ in range(8))
        if get_promocode_by_code(db, generated) is None:
            return generated

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not generate a unique promocode at the moment.",
    )


def _resolve_promocode_code(db: Session, payload: PromocodeCreate) -> str:
    if payload.code_mode == "generate":
        return _generate_unique_promocode_code(db)

    manual_code = normalize_promocode_code(payload.manual_code or "")
    if get_promocode_by_code(db, manual_code) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Promocode with this code already exists.",
        )

    return manual_code


def _build_promocode_read(
    promocode: Promocode,
    *,
    selected_product_ids: list[int],
) -> PromocodeRead:
    return PromocodeRead(
        id=promocode.id,
        seller_id=promocode.seller_id,
        title=promocode.title,
        starts_on=promocode.starts_on,
        ends_on=promocode.ends_on,
        discount_mode=promocode.discount_mode,
        discount_value=promocode.discount_value,
        promo_type=promocode.promo_type,
        audience_type=promocode.audience_type,
        product_scope=promocode.product_scope,
        code=promocode.code,
        status=_resolve_promocode_status(promocode),
        selected_product_ids=selected_product_ids,
        created_at=promocode.created_at,
        updated_at=promocode.updated_at,
    )


def list_seller_promocodes(db: Session, *, seller: Seller) -> list[PromocodeListItem]:
    return [
        PromocodeListItem(
            id=promocode.id,
            title=promocode.title,
            code=promocode.code,
            starts_on=promocode.starts_on,
            ends_on=promocode.ends_on,
            discount_mode=promocode.discount_mode,
            discount_value=promocode.discount_value,
            status=_resolve_promocode_status(promocode),
            created_at=promocode.created_at,
        )
        for promocode in list_promocodes_for_seller(db, seller.id)
    ]


def create_promocode(
    db: Session,
    *,
    seller: Seller,
    payload: PromocodeCreate,
) -> PromocodeRead:
    validate_promocode_dates(payload)

    selected_products = []
    if payload.product_scope == "selected":
        selected_products = list_products_for_seller_by_ids(
            db,
            seller_id=seller.id,
            product_ids=payload.selected_product_ids,
        )
        if len(selected_products) != len(payload.selected_product_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more selected products are unavailable for this seller.",
            )

    promocode = Promocode(
        seller_id=seller.id,
        title=payload.title,
        starts_on=payload.starts_on,
        ends_on=payload.ends_on,
        discount_mode=payload.discount_mode,
        discount_value=payload.discount_value,
        promo_type=payload.promo_type,
        audience_type=payload.audience_type,
        product_scope=payload.product_scope,
        code=_resolve_promocode_code(db, payload),
        product_links=[
            PromocodeProduct(product_id=product.id)
            for product in selected_products
        ],
    )

    add_promocode(db, promocode)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if get_promocode_by_code(db, promocode.code) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Promocode with this code already exists.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Promocode conflicts with an existing record.",
        ) from exc

    db.refresh(promocode)
    return _build_promocode_read(
        promocode,
        selected_product_ids=payload.selected_product_ids if payload.product_scope == "selected" else [],
    )
