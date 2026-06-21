from __future__ import annotations

import unittest
from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.models.product import Product
from app.models.product_item import ProductItem
from app.models.promotion import Promotion
from app.models.promotion_category import PromotionCategory
from app.models.seller import Seller
from app.schemas.promotion import PromotionParticipationCreate
from app.services.promotion import (
    _current_business_date,
    _is_join_open,
    _validate_selected_product,
    create_seller_promotion_participation,
)


def make_promotion(**overrides: object) -> Promotion:
    today = _current_business_date()
    values: dict[str, object] = {
        "slug": "test-promotion",
        "title": "Test promotion",
        "short_description": "Test description",
        "starts_on": today,
        "ends_on": today + timedelta(days=10),
        "join_deadline": today + timedelta(days=5),
        "minimum_discount_percent": 15,
        "minimum_stock_qty": 5,
        "minimum_products": 1,
        "category_scope": "selected",
        "card_tone": "brand",
        "is_featured": False,
        "is_published": True,
    }
    values.update(overrides)
    return Promotion(**values)


def make_product(**overrides: object) -> Product:
    values: dict[str, object] = {
        "seller_id": 1,
        "vendor_code": "TEST-1",
        "title": "Test product",
        "parent_id": 20,
        "is_active": True,
        "items": [
            ProductItem(
                tech_size_name="ONE SIZE",
                price=Decimal("1000"),
                stock_qty=10,
                is_active=True,
            )
        ],
    }
    values.update(overrides)
    return Product(**values)


class PromotionPayloadTests(unittest.TestCase):
    def test_payload_deduplicates_product_ids(self) -> None:
        payload = PromotionParticipationCreate(
            additional_discount_percent=20,
            selected_product_ids=[3, 3, 4],
            price_change_confirmed=True,
        )
        self.assertEqual(payload.selected_product_ids, [3, 4])

    def test_payload_requires_price_confirmation(self) -> None:
        with self.assertRaises(ValidationError):
            PromotionParticipationCreate(
                additional_discount_percent=20,
                selected_product_ids=[3],
                price_change_confirmed=False,
            )


class PromotionBusinessRuleTests(unittest.TestCase):
    def test_join_is_open_during_join_window(self) -> None:
        self.assertTrue(_is_join_open(make_promotion()))

    def test_join_is_closed_after_deadline(self) -> None:
        self.assertFalse(
            _is_join_open(
                make_promotion(
                    join_deadline=_current_business_date() - timedelta(days=1)
                )
            )
        )

    def test_eligible_product_passes_validation(self) -> None:
        _validate_selected_product(
            make_product(),
            promotion=make_promotion(),
            eligible_parent_ids={20},
        )

    def test_low_stock_product_is_rejected(self) -> None:
        product = make_product(
            items=[
                ProductItem(
                    tech_size_name="ONE SIZE",
                    price=Decimal("1000"),
                    stock_qty=2,
                    is_active=True,
                )
            ]
        )
        with self.assertRaises(HTTPException) as context:
            _validate_selected_product(
                product,
                promotion=make_promotion(),
                eligible_parent_ids={20},
            )
        self.assertEqual(context.exception.status_code, 400)

    def test_ineligible_category_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as context:
            _validate_selected_product(
                make_product(parent_id=30),
                promotion=make_promotion(),
                eligible_parent_ids={20},
            )
        self.assertEqual(context.exception.status_code, 400)


class PromotionCreationTests(unittest.TestCase):
    @patch("app.services.promotion.add_promotion_participation")
    @patch("app.services.promotion.list_products_for_seller_by_ids")
    @patch("app.services.promotion.get_participation_for_seller_and_promotion")
    @patch("app.services.promotion.get_published_promotion_by_slug")
    def test_create_participation(
        self,
        get_promotion: MagicMock,
        get_participation: MagicMock,
        list_products: MagicMock,
        add_participation: MagicMock,
    ) -> None:
        promotion = make_promotion(id=10)
        promotion.categories = [
            PromotionCategory(parent_id=20, parent_name="Home")
        ]
        seller = Seller(id=20, username="seller", password_hash="hash", display_name="Seller")
        product = make_product(id=30)
        get_promotion.return_value = promotion
        get_participation.return_value = None
        list_products.return_value = [product]

        def assign_id(_db: object, participation: object) -> object:
            participation.id = 40
            return participation

        add_participation.side_effect = assign_id
        db = MagicMock()
        payload = PromotionParticipationCreate(
            additional_discount_percent=20,
            selected_product_ids=[30],
            price_change_confirmed=True,
        )

        result = create_seller_promotion_participation(
            db,
            seller=seller,
            promotion_slug=promotion.slug,
            payload=payload,
        )

        self.assertEqual(result.id, 40)
        self.assertEqual(result.promotion_slug, promotion.slug)
        self.assertEqual(result.selected_product_ids, [30])
        db.commit.assert_called_once()

    @patch("app.services.promotion.get_participation_for_seller_and_promotion")
    @patch("app.services.promotion.get_published_promotion_by_slug")
    def test_create_rejects_discount_below_promotion_minimum(
        self,
        get_promotion: MagicMock,
        get_participation: MagicMock,
    ) -> None:
        promotion = make_promotion(id=10, minimum_discount_percent=25)
        get_promotion.return_value = promotion
        get_participation.return_value = None
        payload = PromotionParticipationCreate(
            additional_discount_percent=20,
            selected_product_ids=[30],
            price_change_confirmed=True,
        )

        with self.assertRaises(HTTPException) as context:
            create_seller_promotion_participation(
                MagicMock(),
                seller=Seller(
                    id=20,
                    username="seller",
                    password_hash="hash",
                    display_name="Seller",
                ),
                promotion_slug=promotion.slug,
                payload=payload,
            )

        self.assertEqual(context.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
