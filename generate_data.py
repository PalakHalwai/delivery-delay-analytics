import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text

DB_USER = "root"
DB_PASSWORD = ""  # Update if required
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "delivery_analytics"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Clear old data to re-seed cleanly using text()
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    conn.execute(text("TRUNCATE TABLE shipments;"))
    conn.execute(text("TRUNCATE TABLE orders;"))
    conn.execute(text("TRUNCATE TABLE warehouses;"))
    conn.execute(text("TRUNCATE TABLE carriers;"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    conn.commit()

print("Cleared existing tables...")

# Seed Warehouses
warehouses = [
    {"warehouse_id": "WH-01", "region": "North", "processing_capacity_per_day": 300},
    {"warehouse_id": "WH-02", "region": "South", "processing_capacity_per_day": 750},
    {"warehouse_id": "WH-03", "region": "East", "processing_capacity_per_day": 250},
    {"warehouse_id": "WH-04", "region": "West", "processing_capacity_per_day": 600},
]
pd.DataFrame(warehouses).to_sql(
    "warehouses", con=engine, if_exists="append", index=False
)

# Seed Carriers
carriers = [
    {
        "carrier_id": "CR-101",
        "carrier_name": "SwiftExpress",
        "service_level": "Express",
    },
    {
        "carrier_id": "CR-102",
        "carrier_name": "FreightKing",
        "service_level": "Standard",
    },
    {"carrier_id": "CR-103", "carrier_name": "MetroCargo", "service_level": "Standard"},
    {"carrier_id": "CR-104", "carrier_name": "AirRelay", "service_level": "Express"},
]
pd.DataFrame(carriers).to_sql("carriers", con=engine, if_exists="append", index=False)

categories = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Beauty"]
orders, shipments = [], []
start_date = datetime(2026, 1, 1)

for i in range(1, 1001):
    order_id = f"ORD-{i:05d}"
    customer_id = f"CUST-{random.randint(100, 999)}"

    order_ts = start_date + timedelta(
        days=random.randint(0, 200), hours=random.randint(8, 20)
    )
    promised_date = (order_ts + timedelta(days=random.randint(3, 7))).date()
    category = random.choice(categories)
    order_value = round(random.uniform(15.0, 500.0), 2)

    orders.append(
        {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_timestamp": order_ts,
            "promised_delivery_date": promised_date,
            "product_category": category,
            "order_value": order_value,
        }
    )

    selected_wh = random.choice(warehouses)
    selected_cr = random.choice(carriers)

    # Operational Delay Rules
    delay_prob = 0.05

    if selected_wh["processing_capacity_per_day"] < 400:
        delay_prob += 0.30

    if selected_cr["service_level"] == "Standard":
        delay_prob += 0.25

    if order_ts.weekday() in [4, 5]:
        delay_prob += 0.15

    if order_value > 300:
        delay_prob -= 0.10

    if random.random() < max(0.02, delay_prob):
        actual_date = promised_date + timedelta(days=random.randint(1, 5))
    else:
        actual_date = promised_date - timedelta(days=random.randint(0, 2))

    dispatch_ts = order_ts + timedelta(
        days=random.randint(1, 3), hours=random.randint(1, 12)
    )

    shipments.append(
        {
            "shipment_id": f"SHP-{i:05d}",
            "order_id": order_id,
            "warehouse_id": selected_wh["warehouse_id"],
            "carrier_id": selected_cr["carrier_id"],
            "dispatch_timestamp": dispatch_ts,
            "actual_delivery_date": actual_date,
        }
    )

pd.DataFrame(orders).to_sql("orders", con=engine, if_exists="append", index=False)
pd.DataFrame(shipments).to_sql("shipments", con=engine, if_exists="append", index=False)

print(
    "Successfully cleared tables and populated new data with realistic operational patterns!"
)
