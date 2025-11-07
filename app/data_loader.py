import pandas as pd
import os

def load_olist_data(data_path: str):
    print("📦 Loading Olist dataset...")

    orders = pd.read_csv(os.path.join(data_path, "olist_orders_dataset.csv"))
    customers = pd.read_csv(os.path.join(data_path, "olist_customers_dataset.csv"))
    items = pd.read_csv(os.path.join(data_path, "olist_order_items_dataset.csv"))
    products = pd.read_csv(os.path.join(data_path, "olist_products_dataset.csv"))
    payments = pd.read_csv(os.path.join(data_path, "olist_order_payments_dataset.csv"))

    # Merge key data
    merged = orders.merge(customers, on="customer_id", how="left") \
                   .merge(items, on="order_id", how="left") \
                   .merge(products, on="product_id", how="left") \
                   .merge(payments, on="order_id", how="left")

    # Date parsing
    merged["order_purchase_timestamp"] = pd.to_datetime(merged["order_purchase_timestamp"], errors='coerce')

    print("✅ Data loaded successfully.")
    return merged
