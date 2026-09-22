import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

# --- DATABASE CONFIGURATION ---
DB_USER = "root"
DB_PASSWORD = ""  # Put your MySQL root password here inside quotes (leave "" if no password)
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "delivery_analytics"

# Connect using SQLAlchemy
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("Connecting to MySQL and inserting data...")

# --- 1. SEED WAREHOUSES ---
warehouses = [
    {"warehouse_id": "WH-01", "region": "North", "processing_capacity_per_day": 500},
    {"warehouse_id": "WH-02", "region": "South", "processing_capacity_per_day": 750},
    {"warehouse_id": "WH-03", "region": "East", "processing_capacity_per_day": 400},
    {"warehouse_id": "WH-04", "region": "West", "processing_capacity_per_day": 600},
]
df_warehouses = pd.DataFrame(warehouses)
df_warehouses.to_sql("warehouses", con=engine, if_exists="append", index=False)

# --- 2. SEED CARRIERS ---
carriers = [
    {"carrier_id": "CR-101", "carrier_name": "SwiftExpress", "service_level": "Express"},
    {"carrier_id": "CR-102", "carrier_name": "FreightKing", "service_level": "Standard"},
    {"carrier_id": "CR-103", "carrier_name": "MetroCargo", "service_level": "Standard"},
    {"carrier_id": "CR-104", "carrier_name": "AirRelay", "service_level": "Express"},
]
df_carriers = pd.DataFrame(carriers)
df_carriers.to_sql("carriers", con=engine, if_exists="append", index=False)

# --- 3. GENERATE ORDERS & SHIPMENTS ---
categories = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Beauty"]
orders = []
shipments = []

start_date = datetime(2026, 1, 1)

for i in range(1, 1001):
    order_id = f"ORD-{i:05d}"
    customer_id = f"CUST-{random.randint(100, 999)}"

    order_ts = start_date + timedelta(days=random.randint(0, 200), hours=random.randint(8, 20))
    promised_date = (order_ts + timedelta(days=random.randint(3, 7))).date()
    category = random.choice(categories)
    order_value = round(random.uniform(15.0, 500.0), 2)

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "order_timestamp": order_ts,
        "promised_delivery_date": promised_date,
        "product_category": category,
        "order_value": order_value
    })

    dispatch_ts = order_ts + timedelta(days=random.randint(1, 3), hours=random.randint(1, 12))

    # Simulate realistic delay rates
    if random.random() < 0.25:
        actual_date = promised_date + timedelta(days=random.randint(1, 5))
    else:
        actual_date = promised_date - timedelta(days=random.randint(0, 2))

    shipment_id = f"SHP-{i:05d}"
    selected_wh = random.choice(warehouses)["warehouse_id"]
    selected_cr = random.choice(carriers)["carrier_id"]

    shipments.append({
        "shipment_id": shipment_id,
        "order_id": order_id,
        "warehouse_id": selected_wh,
        "carrier_id": selected_cr,
        "dispatch_timestamp": dispatch_ts,
        "actual_delivery_date": actual_date
    })

# Save to MySQL
df_orders = pd.DataFrame(orders)
df_orders.to_sql("orders", con=engine, if_exists="append", index=False)

df_shipments = pd.DataFrame(shipments)
df_shipments.to_sql("shipments", con=engine, if_exists="append", index=False)

print("Successfully inserted 1,000 orders and shipment records into MySQL!")