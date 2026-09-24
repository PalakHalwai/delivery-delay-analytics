# 🚚 Delivery Delay & Supply Chain Operations Analytics Platform

## 📌 Project Overview
An end-to-end operational analytics and predictive modeling platform designed to evaluate and mitigate supply chain delivery delays. Built on a local **MySQL** database, **Python**, **scikit-learn**, and **Streamlit**, this project identifies fulfillment bottlenecks, quantifies revenue at risk, and provides real-time ML-powered delay predictions for incoming shipments.

---

## 🏗️ Architecture & Relational Schema
- **Database**: MySQL relational schema (`orders`, `shipments`, `warehouses`, `carriers`).
- **ETL Ingestion**: Automated data generator script built with `SQLAlchemy` and `Pandas` to model realistic operational bottleneck rules.
- **SQL Analytics**: Multi-join queries analyzing delay rates, carrier on-time delivery benchmarks, and category-level financial risk.
- **Machine Learning**: Random Forest Classifier pipeline (`scikit-learn`) predicting shipment delays with **70%+ recall** on high-risk packages.
- **Interactive Web App**: Interactive dashboard (`Streamlit`) for live SQL KPI monitoring and real-time delivery risk simulation.

---

## 🤖 Machine Learning Model Performance
- **Algorithm**: Random Forest Classifier with `ColumnTransformer` feature preprocessing.
- **Key Features**: Product Category, Order Value, Order Day of Week, Carrier Service Level, Warehouse Region, and Daily Processing Capacity.
- **Metrics**:
  - **ROC-AUC Score**: ~0.74
  - **Delayed Class Recall**: ~0.71

---

## 🖥️ Live Streamlit Dashboard
Launch the interactive web application:
```bash
streamlit run app.py