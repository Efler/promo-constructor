# Схема Базы Данных Promo Constructor

## Таблицы

- `sellers`
- `products`
- `product_items`
- `refresh_sessions`

## Обзор Сущностей

### `sellers`

Аккаунт селлера и контекст владения данными.

### `products`

Карточка товара, принадлежащая селлеру.

### `product_items`

Конкретные товарные позиции внутри карточки товара. Хранит данные уровня размера или item-позиции: размер, штрихкод, цену, скидку, остаток и связанные флаги.

### `refresh_sessions`

Постоянно хранимые refresh-сессии для аутентификации.

## Финальный DDL

```sql
create table sellers (
    id bigserial primary key,
    username varchar(255) not null,
    password_hash varchar(255) not null,
    display_name varchar(255) not null,
    email varchar(255),
    seller_sid uuid,
    is_active boolean not null default true,
    last_login_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint uq_sellers_username unique (username),
    constraint uq_sellers_email unique (email),
    constraint uq_sellers_seller_sid unique (seller_sid)
);

create index ix_sellers_is_active on sellers (is_active);


create table products (
    id bigserial primary key,
    seller_id bigint not null,
    nm_id bigint,
    imt_id bigint,
    vendor_code varchar(100) not null,
    title varchar(255) not null,
    brand varchar(255),
    description text,
    subject_id bigint,
    subject_name varchar(255),
    parent_id bigint,
    parent_name varchar(255),
    kiz_marked boolean not null default false,
    main_photo_url text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint fk_products_seller_id
        foreign key (seller_id)
        references sellers(id)
        on delete cascade,
    constraint uq_products_seller_vendor_code unique (seller_id, vendor_code),
    constraint uq_products_nm_id unique (nm_id)
);

create index ix_products_seller_id on products (seller_id);
create index ix_products_subject_id on products (subject_id);
create index ix_products_parent_id on products (parent_id);
create index ix_products_is_active on products (is_active);


create table product_items (
    id bigserial primary key,
    product_id bigint not null,
    size_id bigint,
    tech_size_name varchar(100) not null default 'ONE SIZE',
    barcode varchar(64),
    price numeric(12, 2) not null,
    discounted_price numeric(12, 2),
    club_discounted_price numeric(12, 2),
    currency_code char(3) not null default 'RUB',
    discount_percent smallint not null default 0,
    club_discount_percent smallint not null default 0,
    editable_size_price boolean not null default false,
    is_bad_turnover boolean not null default false,
    stock_qty integer not null default 0,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint fk_product_items_product_id
        foreign key (product_id)
        references products(id)
        on delete cascade,
    constraint uq_product_items_product_size_name unique (product_id, tech_size_name),
    constraint uq_product_items_product_size_id unique (product_id, size_id),
    constraint uq_product_items_barcode unique (barcode),
    constraint chk_product_items_price_non_negative check (price >= 0),
    constraint chk_product_items_discounted_price_non_negative check (
        discounted_price is null or discounted_price >= 0
    ),
    constraint chk_product_items_club_discounted_price_non_negative check (
        club_discounted_price is null or club_discounted_price >= 0
    ),
    constraint chk_product_items_stock_qty_non_negative check (stock_qty >= 0),
    constraint chk_product_items_discount_percent_range check (
        discount_percent between 0 and 100
    ),
    constraint chk_product_items_club_discount_percent_range check (
        club_discount_percent between 0 and 100
    )
);

create index ix_product_items_product_id on product_items (product_id);
create index ix_product_items_size_id on product_items (size_id);
create index ix_product_items_is_active on product_items (is_active);


create table refresh_sessions (
    id uuid primary key,
    seller_id bigint not null,
    refresh_token_hash varchar(255) not null,
    expires_at timestamptz not null,
    revoked_at timestamptz,
    last_used_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint fk_refresh_sessions_seller_id
        foreign key (seller_id)
        references sellers(id)
        on delete cascade,
    constraint uq_refresh_sessions_refresh_token_hash unique (refresh_token_hash),
    constraint chk_refresh_sessions_expires_after_created check (expires_at >= created_at)
);

create index ix_refresh_sessions_seller_id on refresh_sessions (seller_id);
create index ix_refresh_sessions_expires_at on refresh_sessions (expires_at);
create index ix_refresh_sessions_revoked_at on refresh_sessions (revoked_at);
```

## Манифест Таблиц И Полей

### `sellers`

| Поле | Тип | Смысл |
| --- | --- | --- |
| `id` | `bigserial` | Внутренний идентификатор селлера в Promo Constructor. |
| `username` | `varchar(255)` | Логин для аутентификации. Должен быть уникальным. |
| `password_hash` | `varchar(255)` | Хеш пароля. Сам пароль в базе не хранится. |
| `display_name` | `varchar(255)` | Человекочитаемое имя селлера для UI и API-ответов. |
| `email` | `varchar(255)` | Необязательный email селлера. |
| `seller_sid` | `uuid` | Необязательный идентификатор seller-аккаунта в WB-like домене. Полезен как внешний или бизнес-идентификатор селлера. |
| `is_active` | `boolean` | Активен ли seller-аккаунт. |
| `last_login_at` | `timestamptz` | Время последнего успешного входа. |
| `created_at` | `timestamptz` | Время создания записи. |
| `updated_at` | `timestamptz` | Время последнего обновления записи. |

### `products`

| Поле | Тип | Смысл |
| --- | --- | --- |
| `id` | `bigserial` | Внутренний идентификатор товара. |
| `seller_id` | `bigint` | Владелец товара. Ссылка на `sellers.id`. |
| `nm_id` | `bigint` | Идентификатор карточки товара или артикул товара. |
| `imt_id` | `bigint` | Идентификатор группы или модели карточки товара. |
| `vendor_code` | `varchar(100)` | Артикул продавца. Уникален в рамках одного селлера. |
| `title` | `varchar(255)` | Название товара. |
| `brand` | `varchar(255)` | Бренд товара. |
| `description` | `text` | Описание товара. |
| `subject_id` | `bigint` | Идентификатор предмета. |
| `subject_name` | `varchar(255)` | Название предмета, например тип товара. |
| `parent_id` | `bigint` | Идентификатор родительской категории. |
| `parent_name` | `varchar(255)` | Название родительской категории. |
| `kiz_marked` | `boolean` | Требуется ли для товара маркировка или KIZ-like обработка. |
| `main_photo_url` | `text` | Ссылка на главное изображение товара. |
| `is_active` | `boolean` | Активен ли товар в приложении. |
| `created_at` | `timestamptz` | Время создания записи. |
| `updated_at` | `timestamptz` | Время последнего обновления записи. |

### `product_items`

| Поле | Тип | Смысл |
| --- | --- | --- |
| `id` | `bigserial` | Внутренний идентификатор item-строки. |
| `product_id` | `bigint` | Родительский товар. Ссылка на `products.id`. |
| `size_id` | `bigint` | Идентификатор размера или item-позиции на уровне конкретной строки. |
| `tech_size_name` | `varchar(100)` | Техническое название размера, например `42`, `M` или `ONE SIZE`. |
| `barcode` | `varchar(64)` | Штрихкод конкретной товарной позиции. |
| `price` | `numeric(12,2)` | Базовая цена для этой позиции. |
| `discounted_price` | `numeric(12,2)` | Цена после обычной скидки. |
| `club_discounted_price` | `numeric(12,2)` | Цена после дополнительной клубной скидки. |
| `currency_code` | `char(3)` | Код валюты, обычно `RUB`. |
| `discount_percent` | `smallint` | Процент обычной скидки. |
| `club_discount_percent` | `smallint` | Процент дополнительной клубной скидки. |
| `editable_size_price` | `boolean` | Можно ли управлять ценой отдельно на уровне конкретного item/размера. |
| `is_bad_turnover` | `boolean` | Флаг слабой оборачиваемости или проблемной динамики этой позиции. |
| `stock_qty` | `integer` | Доступный остаток по этой товарной позиции. |
| `is_active` | `boolean` | Активна ли эта item-строка. |
| `created_at` | `timestamptz` | Время создания записи. |
| `updated_at` | `timestamptz` | Время последнего обновления записи. |

### `refresh_sessions`

| Поле | Тип | Смысл |
| --- | --- | --- |
| `id` | `uuid` | Идентификатор сессии. При необходимости позже его можно вкладывать в claims токена. |
| `seller_id` | `bigint` | Селлер, которому принадлежит refresh-сессия. Ссылка на `sellers.id`. |
| `refresh_token_hash` | `varchar(255)` | Хеш refresh-токена, который хранится в cookie. Сам токен в открытом виде хранить нельзя. |
| `expires_at` | `timestamptz` | Момент истечения refresh-токена. |
| `revoked_at` | `timestamptz` | Когда сессия была отозвана. `NULL` означает, что сессия активна. |
| `last_used_at` | `timestamptz` | Время последнего успешного использования refresh-токена. |
| `created_at` | `timestamptz` | Время создания записи. |
| `updated_at` | `timestamptz` | Время последнего обновления записи. |

## Связи

- Один `seller` -> много `products`
- Один `product` -> много `product_items`
- Один `seller` -> много `refresh_sessions`

## Примечания К Реализации

- `updated_at` должен поддерживаться на уровне приложения или слоя SQLAlchemy.
- `refresh_token_hash` нужно сравнивать через хеширование входящего refresh-токена, а не хранить сырой текст токена.
- Access tokens могут оставаться короткоживущими JWT в `httpOnly` cookies.
