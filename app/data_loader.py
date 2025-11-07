import pandas as pd
import os

def load_olist_data(data_path: str):
    """
    Load and merge Olist dataset tables, attach geolocation info for customers and sellers,
    perform cleaning and feature engineering, and return a compact DataFrame ready for DuckDB.
    """
    print("📦 Loading Olist dataset...")

    # --- Load all CSVs
    orders      = pd.read_csv(os.path.join(data_path, "olist_orders_dataset.csv"))
    customers   = pd.read_csv(os.path.join(data_path, "olist_customers_dataset.csv"))
    items       = pd.read_csv(os.path.join(data_path, "olist_order_items_dataset.csv"))
    products    = pd.read_csv(os.path.join(data_path, "olist_products_dataset.csv"))
    payments    = pd.read_csv(os.path.join(data_path, "olist_order_payments_dataset.csv"))
    reviews     = pd.read_csv(os.path.join(data_path, "olist_order_reviews_dataset.csv"))
    sellers     = pd.read_csv(os.path.join(data_path, "olist_sellers_dataset.csv"))
    geolocs     = pd.read_csv(os.path.join(data_path, "olist_geolocation_dataset.csv"))
    translation = pd.read_csv(os.path.join(data_path, "product_category_name_translation.csv"))

    # --- Simplify geolocation (unique by zip prefix)
    geolocs_unique = geolocs.drop_duplicates(subset=["geolocation_zip_code_prefix"]).copy()

    # Merge geolocation into customers
    customers = customers.merge(
        geolocs_unique,
        left_on="customer_zip_code_prefix",
        right_on="geolocation_zip_code_prefix",
        how="left",
    )
    customers.rename(columns={
        "geolocation_lat": "customer_lat",
        "geolocation_lng": "customer_lng",
        "geolocation_city": "customer_geo_city",
        "geolocation_state": "customer_geo_state"
    }, inplace=True)

    # Merge geolocation into sellers
    sellers = sellers.merge(
        geolocs_unique,
        left_on="seller_zip_code_prefix",
        right_on="geolocation_zip_code_prefix",
        how="left",
    )
    sellers.rename(columns={
        "geolocation_lat": "seller_lat",
        "geolocation_lng": "seller_lng",
        "geolocation_city": "seller_geo_city",
        "geolocation_state": "seller_geo_state"
    }, inplace=True)

    # Merge translation for readable product category names
    products = products.merge(translation, on="product_category_name", how="left")

    # --- Merge all datasets
    merged = (
        orders
        .merge(customers, on="customer_id", how="left")
        .merge(items, on="order_id", how="left")
        .merge(products, on="product_id", how="left")
        .merge(payments, on="order_id", how="left")
        .merge(reviews, on="order_id", how="left")
        .merge(sellers, on="seller_id", how="left")
    )

    # --- Parse date columns
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        if col in merged.columns:
            merged[col] = pd.to_datetime(merged[col], errors="coerce")

    # --- Clean missing values
    merged = merged.dropna(subset=["order_purchase_timestamp", "price"])
    merged["price"].fillna(merged["price"].median(), inplace=True)
    merged["payment_value"].fillna(merged["payment_value"].median(), inplace=True)
    merged["freight_value"].fillna(merged["freight_value"].median(), inplace=True)

    # --- Feature engineering
    merged["order_year"]  = merged["order_purchase_timestamp"].dt.year
    merged["order_month"] = merged["order_purchase_timestamp"].dt.month
    merged["delivery_days"] = (
        merged["order_delivered_customer_date"] - merged["order_purchase_timestamp"]
    ).dt.days
    merged["total_order_value"] = merged["price"] + merged["freight_value"]

    # --- Keep relevant columns
    keep_cols = [
        "order_id", "customer_id", "order_status",
        "order_year", "order_month",
        "customer_city", "customer_state",
        "customer_lat", "customer_lng", "customer_geo_city", "customer_geo_state",
        "seller_id", "seller_lat", "seller_lng", "seller_geo_city", "seller_geo_state",
        "product_id", "product_category_name_english",
        "price", "freight_value", "payment_value",
        "review_score", "delivery_days", "total_order_value"
    ]
    merged = merged[[c for c in keep_cols if c in merged.columns]]

    print("✅ Final merged shape:", merged.shape)
    return merged
