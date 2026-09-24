import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import joblib

# Page configuration
st.set_page_config(
    page_title="Delivery Delay Analytics Platform", page_icon="🚚", layout="wide"
)

# --- DATABASE CONNECTION ---
DB_USER = "root"
DB_PASSWORD = ""  # Update if required
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "delivery_analytics"


@st.cache_resource
def get_db_engine():
    return create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


engine = get_db_engine()


# Load Trained ML Pipeline
@st.cache_resource
def load_model():
    return joblib.load("delay_predictor.joblib")


model = load_model()

# Header
st.title("🚚 Delivery Delay & Supply Chain Analytics Dashboard")
st.markdown(
    "Real-time operational monitoring, SQL analytics, and ML-powered delivery risk predictions."
)

# Sidebar Filters
st.sidebar.header("Filter Analytics")
selected_region = st.sidebar.selectbox(
    "Select Warehouse Region", ["All", "North", "South", "East", "West"]
)

# Base SQL Query
query_kpi = """
SELECT
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) AS delayed_shipments,
    ROUND((SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS delay_rate,
    ROUND(SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN o.order_value ELSE 0 END), 2) AS revenue_at_risk
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
"""

if selected_region != "All":
    query_kpi += f" WHERE w.region = '{selected_region}'"

df_kpi = pd.read_sql(query_kpi, con=engine)

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", f"{df_kpi['total_shipments'].iloc[0]:,}")
col2.metric("Delayed Shipments", f"{df_kpi['delayed_shipments'].iloc[0]:,}")
col3.metric("Delay Rate (%)", f"{df_kpi['delay_rate'].iloc[0]}%")
col4.metric("Revenue at Risk ($)", f"${df_kpi['revenue_at_risk'].iloc[0]:,.2f}")

st.divider()

# Tab Navigation
tab1, tab2 = st.tabs(
    ["📊 Analytics & Performance", "🤖 Real-Time Delay Risk Predictor"]
)

# --- TAB 1: ANALYTICS ---
with tab1:
    st.subheader("Carrier & Category Breakdown")

    col_left, col_right = st.columns(2)

    # Carrier Plot
    with col_left:
        query_carrier = """
        SELECT
            c.carrier_name,
            ROUND(100.0 - ((SUM(CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END) * 100.0) / COUNT(s.shipment_id)), 2) AS on_time_rate
        FROM shipments s
        JOIN carriers c ON s.carrier_id = c.carrier_id
        JOIN orders o ON s.order_id = o.order_id
        GROUP BY c.carrier_id, c.carrier_name;
        """
        df_carrier = pd.read_sql(query_carrier, con=engine)

        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(
            data=df_carrier,
            x="carrier_name",
            y="on_time_rate",
            hue="carrier_name",
            palette="viridis",
            legend=False,
            ax=ax,
        )
        ax.set_title("Carrier On-Time Delivery Rate (%)", fontweight="bold")
        ax.set_ylim(0, 100)
        ax.set_ylabel("On-Time Rate (%)")
        st.pyplot(fig)

    # Category Revenue Impact
    with col_right:
        query_category = """
        SELECT
            o.product_category,
            ROUND(SUM(o.order_value), 2) AS delayed_revenue
        FROM shipments s
        JOIN orders o ON s.order_id = o.order_id
        WHERE s.actual_delivery_date > o.promised_delivery_date
        GROUP BY o.product_category
        ORDER BY delayed_revenue DESC;
        """
        df_category = pd.read_sql(query_category, con=engine)

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.barplot(
            data=df_category,
            x="product_category",
            y="delayed_revenue",
            hue="product_category",
            palette="rocket",
            legend=False,
            ax=ax2,
        )
        ax2.set_title("Delayed Revenue Impact ($)", fontweight="bold")
        ax2.set_ylabel("Revenue ($)")
        plt.xticks(rotation=20)
        st.pyplot(fig2)

# --- TAB 2: ML PREDICTOR ---
with tab2:
    st.subheader("Simulate Incoming Order & Predict Delay Risk")

    with st.form("prediction_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            product_category = st.selectbox(
                "Product Category",
                ["Electronics", "Apparel", "Home & Kitchen", "Books", "Beauty"],
            )
            order_value = st.number_input(
                "Order Value ($)", min_value=10.0, max_value=1000.0, value=150.0
            )
            order_day_of_week = st.slider(
                "Day of Week Order Placed (1=Mon, 7=Sun)", 1, 7, 5
            )
            service_level = st.selectbox(
                "Carrier Service Level", ["Express", "Standard"]
            )

        with col_b:
            carrier_name = st.selectbox(
                "Logistics Partner",
                ["SwiftExpress", "FreightKing", "MetroCargo", "AirRelay"],
            )
            region = st.selectbox(
                "Warehouse Region", ["North", "South", "East", "West"]
            )
            processing_capacity = st.selectbox(
                "Warehouse Processing Capacity (Daily)", [250, 300, 600, 750]
            )

        submit_btn = st.form_submit_button("Predict Delay Probability")

    if submit_btn:
        input_data = pd.DataFrame(
            [
                {
                    "product_category": product_category,
                    "order_value": order_value,
                    "order_day_of_week": order_day_of_week,
                    "service_level": service_level,
                    "carrier_name": carrier_name,
                    "region": region,
                    "processing_capacity_per_day": processing_capacity,
                }
            ]
        )

        pred_class = model.predict(input_data)[0]
        pred_prob = model.predict_proba(input_data)[0][1] * 100

        st.divider()
        if pred_class == 1:
            st.error(
                f"⚠️ **HIGH RISK OF DELAY**: Probability of shipment delay is **{pred_prob:.1f}%**"
            )
        else:
            st.success(
                f"✅ **LOW RISK**: Expected to arrive on-time. Delay probability is **{pred_prob:.1f}%**"
            )