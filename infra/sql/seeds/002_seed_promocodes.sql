begin;

-- Test promocodes seed.
-- Depends on:
--   001_seed_sellers_products.sql
--
-- Includes several promocodes for:
--   - seller_roman
--   - seller_alina
--
-- Seed is designed to be re-runnable:
--   - promocodes are upserted by unique code
--   - product mappings for seeded codes are replaced on each run

insert into promocodes (
    seller_id,
    title,
    starts_on,
    ends_on,
    discount_mode,
    discount_value,
    promo_type,
    audience_type,
    product_scope,
    code
)
values
    (
        (select id from sellers where username = 'seller_roman'),
        'Весенняя скидка на футболки',
        current_date + 1,
        current_date + 14,
        'percent',
        15,
        'all_buyers_once',
        'all',
        'selected',
        'ROMAN15'
    ),
    (
        (select id from sellers where username = 'seller_roman'),
        'Промокод на товары для дома',
        current_date + 3,
        current_date + 21,
        'amount',
        300,
        'all_buyers_limited',
        'bought_last_half_year',
        'selected',
        'HOME300'
    ),
    (
        (select id from sellers where username = 'seller_roman'),
        'Архивный промокод Романа',
        current_date - 40,
        current_date - 9,
        'percent',
        10,
        'single_buyer_single_order',
        'all',
        'selected',
        'ROMOLD10'
    ),
    (
        (select id from sellers where username = 'seller_alina'),
        'Скидка на худи',
        current_date + 2,
        current_date + 20,
        'percent',
        20,
        'all_buyers_once',
        'not_bought_last_half_year',
        'selected',
        'ALINA20'
    ),
    (
        (select id from sellers where username = 'seller_alina'),
        'Промокод на весь ассортимент',
        current_date + 1,
        current_date + 30,
        'amount',
        400,
        'all_buyers_limited',
        'all',
        'all',
        'ALINA400'
    ),
    (
        (select id from sellers where username = 'seller_alina'),
        'Просроченный промокод на шоппер',
        current_date - 28,
        current_date - 4,
        'amount',
        250,
        'single_buyer_single_order',
        'bought_last_half_year',
        'selected',
        'ALIBAGOLD'
    )
on conflict (code) do update
set
    seller_id = excluded.seller_id,
    title = excluded.title,
    starts_on = excluded.starts_on,
    ends_on = excluded.ends_on,
    discount_mode = excluded.discount_mode,
    discount_value = excluded.discount_value,
    promo_type = excluded.promo_type,
    audience_type = excluded.audience_type,
    product_scope = excluded.product_scope,
    updated_at = now();

delete from promocode_products
where promocode_id in (
    select id
    from promocodes
    where code in (
        'ROMAN15',
        'HOME300',
        'ROMOLD10',
        'ALINA20',
        'ALINA400',
        'ALIBAGOLD'
    )
);

insert into promocode_products (promocode_id, product_id)
values
    (
        (select id from promocodes where code = 'ROMAN15'),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-TSHIRT-001'
        )
    ),
    (
        (select id from promocodes where code = 'HOME300'),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-PLAID-004'
        )
    ),
    (
        (select id from promocodes where code = 'HOME300'),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-CANDLE-006'
        )
    ),
    (
        (select id from promocodes where code = 'ROMOLD10'),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-MUG-002'
        )
    ),
    (
        (select id from promocodes where code = 'ALINA20'),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_alina'
              and p.vendor_code = 'ALI-HOODIE-001'
        )
    ),
    (
        (select id from promocodes where code = 'ALIBAGOLD'),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_alina'
              and p.vendor_code = 'ALI-BAG-002'
        )
    );

commit;
