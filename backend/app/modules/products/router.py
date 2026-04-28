from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_seller
from app.db.session import get_db
from app.models.product import Product
from app.models.product_item import ProductItem
from app.models.seller import Seller
from app.repositories.product import (
    add_product,
    get_product_by_vendor_code,
    get_product_for_seller,
    list_products_for_seller,
)
from app.schemas.product import ProductBundleCard, ProductCreate, ProductRead

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    products = list_products_for_seller(db, current_seller.id)
    return [ProductRead.model_validate(product) for product in products]


@router.get("/bundle-cards", response_model=list[ProductBundleCard])
def list_products_for_bundles(
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> list[ProductBundleCard]:
    products = list_products_for_seller(db, current_seller.id)
    cards: list[ProductBundleCard] = []

    for product in products:
        active_items = [item for item in product.items if item.is_active]
        if not active_items:
            continue

        discounted_candidates = [item.discounted_price for item in active_items if item.discounted_price is not None]
        cards.append(
            ProductBundleCard(
                id=product.id,
                title=product.title,
                brand=product.brand,
                description=product.description,
                subject_name=product.subject_name,
                parent_name=product.parent_name,
                main_photo_url=product.main_photo_url,
                is_active=product.is_active,
                item_count=len(active_items),
                total_stock_qty=sum(item.stock_qty for item in active_items),
                min_price=min(item.price for item in active_items),
                min_discounted_price=min(discounted_candidates) if discounted_candidates else None,
                max_discount_percent=max(item.discount_percent for item in active_items),
                sizes=[item.tech_size_name for item in active_items],
            )
        )

    return cards


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> ProductRead:
    if get_product_by_vendor_code(db, seller_id=current_seller.id, vendor_code=payload.vendor_code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this vendor_code already exists for the seller.",
        )

    product = Product(
        seller_id=current_seller.id,
        nm_id=payload.nm_id,
        imt_id=payload.imt_id,
        vendor_code=payload.vendor_code,
        title=payload.title,
        brand=payload.brand,
        description=payload.description,
        subject_id=payload.subject_id,
        subject_name=payload.subject_name,
        parent_id=payload.parent_id,
        parent_name=payload.parent_name,
        kiz_marked=payload.kiz_marked,
        main_photo_url=payload.main_photo_url,
        is_active=payload.is_active,
        items=[
            ProductItem(
                size_id=item.size_id,
                tech_size_name=item.tech_size_name,
                barcode=item.barcode,
                price=item.price,
                discounted_price=item.discounted_price,
                club_discounted_price=item.club_discounted_price,
                currency_code=item.currency_code,
                discount_percent=item.discount_percent,
                club_discount_percent=item.club_discount_percent,
                editable_size_price=item.editable_size_price,
                is_bad_turnover=item.is_bad_turnover,
                stock_qty=item.stock_qty,
                is_active=item.is_active,
            )
            for item in payload.items
        ],
    )

    add_product(db, product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product data conflicts with an existing record.",
        ) from exc

    saved_product = get_product_for_seller(db, seller_id=current_seller.id, product_id=product.id)
    if saved_product is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product was created but could not be reloaded.",
        )

    return ProductRead.model_validate(saved_product)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(
    product_id: int,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db),
) -> ProductRead:
    product = get_product_for_seller(db, seller_id=current_seller.id, product_id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return ProductRead.model_validate(product)
