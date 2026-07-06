-- First mart: one row per order with revenue and delivery performance.
with orders as (
    select * from {{ ref('stg_orders') }}
),

items as (
    select
        order_id,
        count(*) as item_count,
        sum(item_price) as gross_merchandise_value,
        sum(freight_value) as total_freight
    from {{ ref('stg_order_items') }}
    group by 1
)

select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.purchased_at,
    o.delivered_at,
    o.estimated_delivery_at,
    coalesce(i.item_count, 0) as item_count,
    coalesce(i.gross_merchandise_value, 0) as gross_merchandise_value,
    coalesce(i.total_freight, 0) as total_freight,
    coalesce(i.gross_merchandise_value, 0)
        + coalesce(i.total_freight, 0) as order_total,
    date_diff(
        'day', o.purchased_at, o.delivered_at
    ) as delivery_days,
    case
        when o.delivered_at is not null
            and o.delivered_at > o.estimated_delivery_at
            then true
        when o.delivered_at is not null then false
    end as is_late_delivery
from orders as o
left join items as i on o.order_id = i.order_id
