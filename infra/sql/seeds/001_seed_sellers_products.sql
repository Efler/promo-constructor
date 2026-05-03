begin;

-- refresh_sessions are not seeded intentionally.
-- They are created and rotated by the auth flow after successful login/refresh.

-- ### SELLERS ACCOUNT PASSWORDS ### --
-- seller_roman -> SellerPass123!
-- seller_alina -> MarketPass123!
-- seller_igor -> PromoPass123!

insert into sellers (
    username,
    password_hash,
    display_name,
    email,
    seller_sid,
    is_active,
    last_login_at
)
values
    (
        'seller_roman',
        '$argon2id$v=19$m=65536,t=3,p=4$Kccea87+k9uVxoB+Y8aUjw$u/McfvKfdOfvcwLOAjmebN88cu7jVQjeBHOoCPQ6FPs',
        'Roman Volkov',
        'roman.volkov@promo.local',
        '11111111-1111-1111-1111-111111111111',
        true,
        now()
    ),
    (
        'seller_alina',
        '$argon2id$v=19$m=65536,t=3,p=4$/EDv+ByXbeML9F42S9uDRQ$MQhNNlQ3RFkx8K9PBHIexP5m0oKIL6mXe7nxqNq1ipo',
        'Alina Smirnova',
        'alina.smirnova@promo.local',
        '22222222-2222-2222-2222-222222222222',
        true,
        now()
    ),
    (
        'seller_igor',
        '$argon2id$v=19$m=65536,t=3,p=4$8qlEgfKepCeqJkJxlnNxEg$Z1AU1cMTjcqzZuRKCZB8V9YldhI/sTtZb+ZzPtFlFD0',
        'Igor Sokolov',
        'igor.sokolov@promo.local',
        '33333333-3333-3333-3333-333333333333',
        true,
        now()
    )
on conflict (username) do update
set
    password_hash = excluded.password_hash,
    display_name = excluded.display_name,
    email = excluded.email,
    seller_sid = excluded.seller_sid,
    is_active = excluded.is_active,
    last_login_at = excluded.last_login_at,
    updated_at = now();

insert into products (
    seller_id,
    nm_id,
    imt_id,
    vendor_code,
    title,
    brand,
    description,
    subject_id,
    subject_name,
    parent_id,
    parent_name,
    kiz_marked,
    main_photo_url,
    is_active
)
values
    (
        (select id from sellers where username = 'seller_roman'),
        710000101,
        810000101,
        'ROM-TSHIRT-001',
        'Базовая хлопковая футболка',
        'Северный берег',
        'Классическая хлопковая футболка унисекс для повседневного ассортимента.',
        101,
        'Футболки',
        10,
        'Одежда',
        false,
        'https://images.promo.local/products/rom-tshirt-001.jpg',
        true
    ),
    (
        (select id from sellers where username = 'seller_roman'),
        710000102,
        810000102,
        'ROM-MUG-002',
        'Керамическая кружка',
        'Домашний уют',
        'Белая керамическая кружка с минималистичным принтом для дома и офиса.',
        202,
        'Кружки',
        20,
        'Товары для дома',
        false,
        'https://images.promo.local/products/rom-mug-002.jpg',
        true
    ),
    (
        (select id from sellers where username = 'seller_alina'),
        710000201,
        810000201,
        'ALI-HOODIE-001',
        'Оверсайз-худи из флиса',
        'Урбан Нест',
        'Теплое оверсайз-худи для осенних и зимних коллекций.',
        103,
        'Худи',
        10,
        'Одежда',
        false,
        'https://images.promo.local/products/ali-hoodie-001.jpg',
        true
    ),
    (
        (select id from sellers where username = 'seller_alina'),
        710000202,
        810000202,
        'ALI-BAG-002',
        'Холщовая сумка-шоппер',
        'Урбан Нест',
        'Многоразовая холщовая сумка-шоппер с усиленными ручками.',
        301,
        'Сумки',
        30,
        'Аксессуары',
        false,
        'https://images.promo.local/products/ali-bag-002.jpg',
        true
    ),
    (
        (select id from sellers where username = 'seller_igor'),
        710000301,
        810000301,
        'IGO-LAMP-001',
        'Светодиодная настольная лампа',
        'Брайт Форм',
        'Компактная светодиодная настольная лампа с регулируемым углом наклона и теплым режимом света.',
        401,
        'Настольные лампы',
        40,
        'Освещение',
        false,
        'https://images.promo.local/products/igo-lamp-001.jpg',
        true
    )
on conflict (seller_id, vendor_code) do update
set
    nm_id = excluded.nm_id,
    imt_id = excluded.imt_id,
    title = excluded.title,
    brand = excluded.brand,
    description = excluded.description,
    subject_id = excluded.subject_id,
    subject_name = excluded.subject_name,
    parent_id = excluded.parent_id,
    parent_name = excluded.parent_name,
    kiz_marked = excluded.kiz_marked,
    main_photo_url = excluded.main_photo_url,
    is_active = excluded.is_active,
    updated_at = now();

insert into product_items (
    product_id,
    size_id,
    tech_size_name,
    barcode,
    price,
    discounted_price,
    club_discounted_price,
    currency_code,
    discount_percent,
    club_discount_percent,
    editable_size_price,
    is_bad_turnover,
    stock_qty,
    is_active
)
values
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_roman' and p.vendor_code = 'ROM-TSHIRT-001'),
        501001,
        'M',
        '4607001000011',
        1290.00,
        1090.00,
        990.00,
        'RUB',
        16,
        23,
        true,
        false,
        18,
        true
    ),
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_roman' and p.vendor_code = 'ROM-TSHIRT-001'),
        501002,
        'L',
        '4607001000012',
        1290.00,
        1150.00,
        1050.00,
        'RUB',
        11,
        19,
        true,
        false,
        9,
        true
    ),
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_roman' and p.vendor_code = 'ROM-MUG-002'),
        502001,
        'ONE SIZE',
        '4607001000021',
        590.00,
        490.00,
        null,
        'RUB',
        17,
        0,
        false,
        false,
        32,
        true
    ),
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_alina' and p.vendor_code = 'ALI-HOODIE-001'),
        601001,
        'S',
        '4607002000011',
        3490.00,
        2990.00,
        2790.00,
        'RUB',
        14,
        20,
        true,
        false,
        7,
        true
    ),
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_alina' and p.vendor_code = 'ALI-HOODIE-001'),
        601002,
        'M',
        '4607002000012',
        3490.00,
        3090.00,
        2890.00,
        'RUB',
        11,
        17,
        true,
        false,
        11,
        true
    ),
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_alina' and p.vendor_code = 'ALI-BAG-002'),
        602001,
        'ONE SIZE',
        '4607002000021',
        1190.00,
        990.00,
        null,
        'RUB',
        17,
        0,
        false,
        false,
        24,
        true
    ),
    (
        (select p.id from products p join sellers s on s.id = p.seller_id where s.username = 'seller_igor' and p.vendor_code = 'IGO-LAMP-001'),
        701001,
        'ONE SIZE',
        '4607003000011',
        2590.00,
        2290.00,
        2190.00,
        'RUB',
        12,
        15,
        false,
        false,
        13,
        true
    )
on conflict (barcode) do update
set
    product_id = excluded.product_id,
    size_id = excluded.size_id,
    tech_size_name = excluded.tech_size_name,
    price = excluded.price,
    discounted_price = excluded.discounted_price,
    club_discounted_price = excluded.club_discounted_price,
    currency_code = excluded.currency_code,
    discount_percent = excluded.discount_percent,
    club_discount_percent = excluded.club_discount_percent,
    editable_size_price = excluded.editable_size_price,
    is_bad_turnover = excluded.is_bad_turnover,
    stock_qty = excluded.stock_qty,
    is_active = excluded.is_active,
    updated_at = now();

commit;
