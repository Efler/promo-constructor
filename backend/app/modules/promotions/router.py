from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_seller
from app.db.session import get_db
from app.models.seller import Seller
from app.schemas.promotion import (
    PromotionCatalogItem,
    PromotionParticipationCreate,
    PromotionParticipationCreateResponse,
    PromotionParticipationRead,
)
from app.services.promotion import (
    create_seller_promotion_participation,
    get_marketplace_promotion,
    list_marketplace_promotions,
    list_seller_promotion_participations,
)

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("", response_model=list[PromotionCatalogItem])
def list_promotions(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> list[PromotionCatalogItem]:
    del current_seller
    return list_marketplace_promotions(db)


@router.get("/participations", response_model=list[PromotionParticipationRead])
def list_promotion_participations(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> list[PromotionParticipationRead]:
    return list_seller_promotion_participations(db, seller=current_seller)


@router.get("/{promotion_slug}", response_model=PromotionCatalogItem)
def read_promotion(
    promotion_slug: str,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> PromotionCatalogItem:
    del current_seller
    return get_marketplace_promotion(db, promotion_slug=promotion_slug)


@router.post(
    "/{promotion_slug}/participations",
    response_model=PromotionParticipationCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_promotion_participation(
    promotion_slug: str,
    payload: PromotionParticipationCreate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> PromotionParticipationCreateResponse:
    participation = create_seller_promotion_participation(
        db,
        seller=current_seller,
        promotion_slug=promotion_slug,
        payload=payload,
    )
    return PromotionParticipationCreateResponse(
        message="Promotion participation created.",
        participation=participation,
    )
