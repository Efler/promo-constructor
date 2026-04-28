from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_seller
from app.schemas.auth import SellerIdentity

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get("/me")
def read_seller_profile(
    current_seller: SellerIdentity = Depends(get_current_seller),
) -> dict[str, SellerIdentity]:
    return {"seller": current_seller}
