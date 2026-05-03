from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_seller
from app.db.session import get_db
from app.models.seller import Seller
from app.schemas.promocode import (
    PromocodeCodeAvailability,
    PromocodeCreate,
    PromocodeCreateResponse,
    PromocodeListItem,
)
from app.services.promocode import (
    create_promocode,
    is_promocode_code_available,
    list_seller_promocodes,
    normalize_promocode_code,
)

router = APIRouter(prefix="/promocodes", tags=["promocodes"])


@router.get("", response_model=list[PromocodeListItem])
def list_promocodes(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> list[PromocodeListItem]:
    return list_seller_promocodes(db, seller=current_seller)


@router.get("/code-availability", response_model=PromocodeCodeAvailability)
def check_promocode_code_availability(
    code: str = Query(min_length=1, max_length=15),
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> PromocodeCodeAvailability:
    del current_seller
    normalized_code = normalize_promocode_code(code)
    return PromocodeCodeAvailability(
        code=code,
        normalized_code=normalized_code,
        is_available=is_promocode_code_available(db, normalized_code),
    )


@router.post("", response_model=PromocodeCreateResponse, status_code=status.HTTP_201_CREATED)
def create_promocode_route(
    payload: PromocodeCreate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> PromocodeCreateResponse:
    promocode = create_promocode(db, seller=current_seller, payload=payload)
    return PromocodeCreateResponse(
        message="Promocode created.",
        promocode=promocode,
    )
