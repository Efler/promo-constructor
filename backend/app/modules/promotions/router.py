from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_seller
from app.models.seller import Seller

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("")
def list_promotions(current_seller: Seller = Depends(get_current_seller)) -> dict[str, object]:
    return {
        "items": [],
        "seller": current_seller.username,
        "message": "Promotions module scaffold is ready for future campaign flows.",
    }
