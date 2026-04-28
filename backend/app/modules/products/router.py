from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_seller
from app.schemas.auth import SellerIdentity

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(current_seller: SellerIdentity = Depends(get_current_seller)) -> dict[str, object]:
    return {
        "items": [],
        "seller": current_seller.username,
        "message": "Products module scaffold is ready for future seller inventory data.",
    }
