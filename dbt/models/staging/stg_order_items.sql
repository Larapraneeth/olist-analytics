with source as (
    select * from {{ source('raw', 'order_items') }}
)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    cast(shipping_limit_date as timestamp) as shipping_limit_at,
    cast(price as decimal(10, 2)) as item_price,
    cast(freight_value as decimal(10, 2)) as freight_value
from source
