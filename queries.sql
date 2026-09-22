USE delivery_analytics;

-- ============================================================
-- QUERY 1: Overall Delivery Delay Rate (%)
-- Key Metric: Percentage of orders delivered past promised date
-- ============================================================
SELECT
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) AS delayed_shipments,
    ROUND(
        (SUM(CASE WHEN actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) * 100.0) / COUNT(*),
        2
    ) AS delay_rate_percentage
FROM shipments s
JOIN orders o ON s.order_id = o.order_id;


-- ============================================================
-- QUERY 2: Carrier Performance & On-Time Delivery Index
-- Identifies slow vs. reliable carriers
-- ============================================================
SELECT
    c.carrier_name,
    c.service_level,
    COUNT(s.shipment_id) AS total_deliveries,
    SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND(
        100.0 - ((SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) * 100.0) / COUNT(s.shipment_id)),
        2
    ) AS on_time_delivery_rate
FROM shipments s
JOIN carriers c ON s.carrier_id = c.carrier_id
JOIN orders o ON s.order_id = o.order_id
GROUP BY c.carrier_id, c.carrier_name, c.service_level
ORDER BY on_time_delivery_rate ASC;


-- ============================================================
-- QUERY 3: Regional Warehouse Delay Analysis
-- Uncovers regional fulfillment bottlenecks
-- ============================================================
SELECT
    w.region,
    w.warehouse_id,
    w.processing_capacity_per_day,
    COUNT(s.shipment_id) AS orders_handled,
    SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) AS total_delays,
    ROUND(
        (SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) * 100.0) / COUNT(s.shipment_id),
        2
    ) AS warehouse_delay_rate
FROM shipments s
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
JOIN orders o ON s.order_id = o.order_id
GROUP BY w.warehouse_id, w.region, w.processing_capacity_per_day
ORDER BY warehouse_delay_rate DESC;


-- ============================================================
-- QUERY 4: Revenue Impact of Delivery Delays
-- Calculates total order value impacted by late deliveries
-- ============================================================
SELECT
    o.product_category,
    COUNT(o.order_id) AS delayed_order_count,
    ROUND(SUM(o.order_value), 2) AS delayed_revenue_at_risk
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
WHERE s.actual_delivery_date > o.promised_delivery_date
GROUP BY o.product_category
ORDER BY delayed_revenue_at_risk DESC;