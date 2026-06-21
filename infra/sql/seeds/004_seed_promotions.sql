begin;

-- Marketplace promotions catalog seed.
-- Depends on:
--   Alembic revision 20260621_0004
--
-- Covers active and upcoming campaigns for roughly the next 6-8 weeks.
--
-- Seed is designed to be re-runnable:
--   - promotions are upserted by unique slug
--   - benefits and category mappings are replaced on each run

insert into promotions (
    slug,
    title,
    short_description,
    starts_on,
    ends_on,
    join_deadline,
    minimum_discount_percent,
    minimum_stock_qty,
    minimum_products,
    category_scope,
    card_tone,
    is_featured,
    is_published
)
values
    (
        'summer-hit',
        'Хиты лета',
        'Большая сезонная распродажа с дополнительным продвижением товаров в поиске и рекомендациях.',
        current_date - 3,
        current_date + 11,
        current_date + 5,
        15,
        5,
        2,
        'all',
        'brand',
        true,
        true
    ),
    (
        'fast-weekend',
        'Быстрые выходные',
        'Короткая акция для товаров с хорошим остатком и быстрой конверсией в заказ.',
        current_date + 2,
        current_date + 5,
        current_date + 1,
        12,
        3,
        1,
        'all',
        'orange',
        false,
        true
    ),
    (
        'home-comfort',
        'Неделя домашнего уюта',
        'Тематическая подборка товаров для дома, интерьера и освещения.',
        current_date + 9,
        current_date + 21,
        current_date + 7,
        20,
        8,
        2,
        'selected',
        'teal',
        true,
        true
    ),
    (
        'fashion-focus',
        'Фокус на стиль',
        'Продвижение одежды и аксессуаров в специальной модной витрине маркетплейса.',
        current_date + 18,
        current_date + 31,
        current_date + 15,
        25,
        5,
        1,
        'selected',
        'grape',
        false,
        true
    ),
    (
        'mega-price-drop',
        'Мегаскидки месяца',
        'Главная распродажа месяца для товаров с глубокими скидками и достаточным запасом.',
        current_date + 30,
        current_date + 45,
        current_date + 27,
        30,
        12,
        3,
        'all',
        'blue',
        true,
        true
    )
on conflict (slug) do update
set
    title = excluded.title,
    short_description = excluded.short_description,
    starts_on = excluded.starts_on,
    ends_on = excluded.ends_on,
    join_deadline = excluded.join_deadline,
    minimum_discount_percent = excluded.minimum_discount_percent,
    minimum_stock_qty = excluded.minimum_stock_qty,
    minimum_products = excluded.minimum_products,
    category_scope = excluded.category_scope,
    card_tone = excluded.card_tone,
    is_featured = excluded.is_featured,
    is_published = excluded.is_published,
    updated_at = now();

delete from promotion_benefits
where promotion_id in (
    select id
    from promotions
    where slug in (
        'summer-hit',
        'fast-weekend',
        'home-comfort',
        'fashion-focus',
        'mega-price-drop'
    )
);

insert into promotion_benefits (promotion_id, position, description)
values
    (
        (select id from promotions where slug = 'summer-hit'),
        1,
        'Приоритетная витрина сезонных предложений'
    ),
    (
        (select id from promotions where slug = 'summer-hit'),
        2,
        'Дополнительные показы в поиске'
    ),
    (
        (select id from promotions where slug = 'fast-weekend'),
        1,
        'Подборка выгодных предложений на главной'
    ),
    (
        (select id from promotions where slug = 'fast-weekend'),
        2,
        'Акционная плашка на весь период'
    ),
    (
        (select id from promotions where slug = 'home-comfort'),
        1,
        'Размещение в тематической подборке'
    ),
    (
        (select id from promotions where slug = 'home-comfort'),
        2,
        'Повышенный приоритет в рекомендациях'
    ),
    (
        (select id from promotions where slug = 'fashion-focus'),
        1,
        'Попадание в модные подборки'
    ),
    (
        (select id from promotions where slug = 'fashion-focus'),
        2,
        'Больше показов в похожих товарах'
    ),
    (
        (select id from promotions where slug = 'mega-price-drop'),
        1,
        'Максимальный охват акционной аудитории'
    ),
    (
        (select id from promotions where slug = 'mega-price-drop'),
        2,
        'Отдельный лендинг распродажи'
    );

delete from promotion_categories
where promotion_id in (
    select id
    from promotions
    where slug in (
        'summer-hit',
        'fast-weekend',
        'home-comfort',
        'fashion-focus',
        'mega-price-drop'
    )
);

insert into promotion_categories (promotion_id, parent_id, parent_name)
values
    (
        (select id from promotions where slug = 'home-comfort'),
        20,
        'Товары для дома'
    ),
    (
        (select id from promotions where slug = 'home-comfort'),
        40,
        'Освещение'
    ),
    (
        (select id from promotions where slug = 'fashion-focus'),
        10,
        'Одежда'
    ),
    (
        (select id from promotions where slug = 'fashion-focus'),
        30,
        'Аксессуары'
    );

commit;
