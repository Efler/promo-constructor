from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_seller
from app.models.seller import Seller

router = APIRouter(prefix="/bundles", tags=["bundles"])


@router.get("")
def list_bundles(current_seller: Seller = Depends(get_current_seller)) -> dict[str, object]:
    return {
        "items": [],
        "seller": current_seller.username,
        "message": "Bundles module scaffold is ready for future business logic.",
    }
