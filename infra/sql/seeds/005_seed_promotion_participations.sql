begin;

-- Seller promotion participation seed.
-- Depends on:
--   001_seed_sellers_products.sql
--   004_seed_promotions.sql
--
-- Includes active and scheduled participations for:
--   - seller_roman
--   - seller_alina
--
-- Seed is designed to be re-runnable:
--   - participations are upserted by seller/promotion
--   - selected product mappings are replaced on each run

insert into promotion_participations (
    promotion_id,
    seller_id,
    additional_discount_percent,
    price_change_confirmed_at,
    joined_at
)
values
    (
        (select id from promotions where slug = 'summer-hit'),
        (select id from sellers where username = 'seller_roman'),
        18,
        now() - interval '2 days',
        now() - interval '2 days'
    ),
    (
        (select id from promotions where slug = 'home-comfort'),
        (select id from sellers where username = 'seller_roman'),
        22,
        now(),
        now()
    ),
    (
        (select id from promotions where slug = 'fast-weekend'),
        (select id from sellers where username = 'seller_alina'),
        15,
        now(),
        now()
    ),
    (
        (select id from promotions where slug = 'fashion-focus'),
        (select id from sellers where username = 'seller_alina'),
        27,
        now(),
        now()
    )
on conflict (seller_id, promotion_id) do update
set
    additional_discount_percent = excluded.additional_discount_percent,
    price_change_confirmed_at = excluded.price_change_confirmed_at,
    joined_at = excluded.joined_at,
    updated_at = now();

delete from promotion_participation_products
where participation_id in (
    select pp.id
    from promotion_participations pp
    join sellers s on s.id = pp.seller_id
    join promotions p on p.id = pp.promotion_id
    where (s.username, p.slug) in (
        ('seller_roman', 'summer-hit'),
        ('seller_roman', 'home-comfort'),
        ('seller_alina', 'fast-weekend'),
        ('seller_alina', 'fashion-focus')
    )
);

insert into promotion_participation_products (participation_id, product_id)
values
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_roman'
              and p.slug = 'summer-hit'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-TSHIRT-001'
        )
    ),
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_roman'
              and p.slug = 'summer-hit'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-MUG-002'
        )
    ),
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_roman'
              and p.slug = 'home-comfort'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-MUG-002'
        )
    ),
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_roman'
              and p.slug = 'home-comfort'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_roman'
              and p.vendor_code = 'ROM-PLAID-004'
        )
    ),
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_alina'
              and p.slug = 'fast-weekend'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_alina'
              and p.vendor_code = 'ALI-BAG-002'
        )
    ),
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_alina'
              and p.slug = 'fashion-focus'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_alina'
              and p.vendor_code = 'ALI-HOODIE-001'
        )
    ),
    (
        (
            select pp.id
            from promotion_participations pp
            join sellers s on s.id = pp.seller_id
            join promotions p on p.id = pp.promotion_id
            where s.username = 'seller_alina'
              and p.slug = 'fashion-focus'
        ),
        (
            select p.id
            from products p
            join sellers s on s.id = p.seller_id
            where s.username = 'seller_alina'
              and p.vendor_code = 'ALI-BAG-002'
        )
    );

commit;
