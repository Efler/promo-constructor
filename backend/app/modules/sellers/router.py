from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_seller
from app.models.seller import Seller
from app.schemas.seller import SellerRead

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get("/me", response_model=SellerRead)
def read_seller_profile(current_seller: Seller = Depends(get_current_seller)) -> SellerRead:
    return SellerRead.model_validate(current_seller)
