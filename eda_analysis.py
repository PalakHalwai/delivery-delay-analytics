import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# --- DATABASE CONFIGURATION ---
DB_USER = "root"
DB_PASSWORD = ""  # Update if you set a password
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "delivery_analytics"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "Arial"

# --- 1. QUERY CARRIER PERFORMANCE ---
query_carrier = """
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
GROUP BY c.carrier_id, c.carrier_name, c.service_level;
"""

df_carrier = pd.read_sql(query_carrier, con=engine)

# Plot Carrier On-Time Performance
plt.figure(figsize=(8, 5))
ax = sns.barplot(
    data=df_carrier,
    x="carrier_name",
    y="on_time_delivery_rate",
    hue="carrier_name",
    palette="viridis",
    legend=False,
)
plt.title("Carrier On-Time Delivery Rate (%)", fontsize=14, fontweight="bold")
plt.xlabel("Carrier Name", fontsize=12)
plt.ylabel("On-Time Rate (%)", fontsize=12)
plt.ylim(0, 100)

for p in ax.patches:
    ax.annotate(
        f"{p.get_height():.1f}%",
        (p.get_x() + p.get_width() / 2.0, p.get_height() - 8),
        ha="center",
        va="center",
        color="white",
        fontweight="bold",
        fontsize=11,
    )

plt.tight_layout()
plt.savefig("carrier_performance.png", dpi=300)
print("Saved carrier_performance.png")
plt.show()

# --- 2. QUERY REVENUE AT RISK ---
query_revenue = """
SELECT
    o.product_category,
    ROUND(SUM(o.order_value), 2) AS delayed_revenue_at_risk
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
WHERE s.actual_delivery_date > o.promised_delivery_date
GROUP BY o.product_category
ORDER BY delayed_revenue_at_risk DESC;
"""

df_revenue = pd.read_sql(query_revenue, con=engine)

# Plot Revenue Impact
plt.figure(figsize=(9, 5))
ax2 = sns.barplot(
    data=df_revenue,
    x="product_category",
    y="delayed_revenue_at_risk",
    hue="product_category",
    palette="rocket",
    legend=False,
)
plt.title(
    "Delayed Revenue Impact by Product Category ($)", fontsize=14, fontweight="bold"
)
plt.xlabel("Product Category", fontsize=12)
plt.ylabel("Delayed Revenue ($)", fontsize=12)

for p in ax2.patches:
    ax2.annotate(
        f"${p.get_height():,.2f}",
        (p.get_x() + p.get_width() / 2.0, p.get_height() / 2),
        ha="center",
        va="center",
        color="white",
        fontweight="bold",
        fontsize=10,
    )

plt.tight_layout()
plt.savefig("revenue_at_risk.png", dpi=300)
print("Saved revenue_at_risk.png")
plt.show()
