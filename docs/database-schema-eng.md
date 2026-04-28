# Promo Constructor Database Schema

## Tables

- `sellers`
- `products`
- `product_items`
- `refresh_sessions`

## Entity Overview

### `sellers`

Seller account and ownership context.

### `products`

Product card owned by a seller.

### `product_items`

Concrete item rows inside a product card. Stores size/item-level data: size, barcode, price, discount, stock, and related flags.

### `refresh_sessions`

Persisted refresh-token sessions for authentication.

## Final DDL

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

## Table and Field Manifest

### `sellers`

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `bigserial` | Internal seller identifier in Promo Constructor. |
| `username` | `varchar(255)` | Login used for authentication. Must be unique. |
| `password_hash` | `varchar(255)` | Hashed password. Raw password is never stored. |
| `display_name` | `varchar(255)` | Human-readable seller name for UI and API responses. |
| `email` | `varchar(255)` | Optional seller email. |
| `seller_sid` | `uuid` | Optional seller account identifier in the WB-like domain. Useful as an external/business seller reference. |
| `is_active` | `boolean` | Whether the seller account is active. |
| `last_login_at` | `timestamptz` | Time of the last successful login. |
| `created_at` | `timestamptz` | Row creation timestamp. |
| `updated_at` | `timestamptz` | Row update timestamp. |

### `products`

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `bigserial` | Internal product identifier. |
| `seller_id` | `bigint` | Owner seller. References `sellers.id`. |
| `nm_id` | `bigint` | Product card/article identifier. |
| `imt_id` | `bigint` | Group/model identifier for the product card. |
| `vendor_code` | `varchar(100)` | Seller article code. Unique within one seller. |
| `title` | `varchar(255)` | Product title. |
| `brand` | `varchar(255)` | Product brand. |
| `description` | `text` | Product description. |
| `subject_id` | `bigint` | Subject identifier. |
| `subject_name` | `varchar(255)` | Subject name, for example a product type. |
| `parent_id` | `bigint` | Parent category identifier. |
| `parent_name` | `varchar(255)` | Parent category name. |
| `kiz_marked` | `boolean` | Whether the product is marked / requires KIZ-like handling. |
| `main_photo_url` | `text` | Main product image URL. |
| `is_active` | `boolean` | Whether the product is active in the application. |
| `created_at` | `timestamptz` | Row creation timestamp. |
| `updated_at` | `timestamptz` | Row update timestamp. |

### `product_items`

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `bigserial` | Internal item-row identifier. |
| `product_id` | `bigint` | Parent product. References `products.id`. |
| `size_id` | `bigint` | Size/item identifier at the item level. |
| `tech_size_name` | `varchar(100)` | Technical size label, for example `42`, `M`, or `ONE SIZE`. |
| `barcode` | `varchar(64)` | Barcode of the concrete item row. |
| `price` | `numeric(12,2)` | Base price for this item. |
| `discounted_price` | `numeric(12,2)` | Price after the regular discount. |
| `club_discounted_price` | `numeric(12,2)` | Price after an additional club discount. |
| `currency_code` | `char(3)` | Currency code, usually `RUB`. |
| `discount_percent` | `smallint` | Regular discount percent. |
| `club_discount_percent` | `smallint` | Extra club discount percent. |
| `editable_size_price` | `boolean` | Whether price is managed per item/size separately. |
| `is_bad_turnover` | `boolean` | Flag for weak turnover / problematic item dynamics. |
| `stock_qty` | `integer` | Available stock quantity for this item row. |
| `is_active` | `boolean` | Whether this item row is active. |
| `created_at` | `timestamptz` | Row creation timestamp. |
| `updated_at` | `timestamptz` | Row update timestamp. |

### `refresh_sessions`

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | `uuid` | Session identifier. Can also be embedded into token claims if needed later. |
| `seller_id` | `bigint` | Seller who owns the refresh session. References `sellers.id`. |
| `refresh_token_hash` | `varchar(255)` | Hash of the refresh token stored in the cookie. The raw token should not be stored. |
| `expires_at` | `timestamptz` | Refresh-token expiration moment. |
| `revoked_at` | `timestamptz` | When the session was revoked. `NULL` means active. |
| `last_used_at` | `timestamptz` | Last successful refresh usage time. |
| `created_at` | `timestamptz` | Row creation timestamp. |
| `updated_at` | `timestamptz` | Row update timestamp. |

## Relationships

- One `seller` -> many `products`
- One `product` -> many `product_items`
- One `seller` -> many `refresh_sessions`

## Implementation Notes

- `updated_at` should be maintained by the application or SQLAlchemy layer.
- `refresh_token_hash` should be compared by hashing the incoming refresh token value, not by storing raw token text.
- Access tokens can stay short-lived JWTs in `httpOnly` cookies.
