import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# --- 1. DATABASE CONNECTION ---
DB_USER = "root"
DB_PASSWORD = ""  # Update if required
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "delivery_analytics"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- 2. QUERY & FEATURE ENGINEERING ---
query = """
SELECT
    o.product_category,
    o.order_value,
    DAYOFWEEK(o.order_timestamp) AS order_day_of_week,
    c.service_level,
    c.carrier_name,
    w.region,
    w.processing_capacity_per_day,
    DATEDIFF(s.actual_delivery_date, o.promised_delivery_date) AS delay_days,
    CASE WHEN s.actual_delivery_date > o.promised_delivery_date THEN 1 ELSE 0 END AS is_delayed
FROM shipments s
JOIN orders o ON s.order_id = o.order_id
JOIN carriers c ON s.carrier_id = c.carrier_id
JOIN warehouses w ON s.warehouse_id = w.warehouse_id;
"""

df = pd.read_sql(query, con=engine)

# Features & Target
X = df[["product_category", "order_value", "order_day_of_week", "service_level", "carrier_name", "region", "processing_capacity_per_day"]]
y = df["is_delayed"]

# --- 3. PREPROCESSING & PIPELINE BUILD ---
categorical_features = ["product_category", "service_level", "carrier_name", "region"]
numeric_features = ["order_value", "order_day_of_week", "processing_capacity_per_day"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ]
)

model_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"))
])

# --- 4. TRAIN & EVALUATE ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model_pipeline.fit(X_train, y_train)
y_pred = model_pipeline.predict(X_test)
y_proba = model_pipeline.predict_proba(X_test)[:, 1]

print("=== MODEL EVALUATION REPORT ===")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

# Save Model Pipeline
joblib.dump(model_pipeline, "delay_predictor.joblib")
print("Saved trained model to delay_predictor.joblib")