# app/data_loader.py
import pandas as pd
import os

def load_olist_data(data_path: str):
    """
    Load all Olist CSVs from data_path, merge them into a single DataFrame,
    convert important columns to numeric/datetime, and return the merged frame.
    """
    print("📦 Loading Olist dataset (full merge with geolocation & dimensions)...")

    # Load CSVs (safe reads)
    def read_csv_safe(p):
        try:
            return pd.read_csv(p)
        except Exception as e:
            print(f"⚠️ Could not read {p}: {e}")
            return pd.DataFrame()

    orders      = read_csv_safe(os.path.join(data_path, "olist_orders_dataset.csv"))
    customers   = read_csv_safe(os.path.join(data_path, "olist_customers_dataset.csv"))
    items       = read_csv_safe(os.path.join(data_path, "olist_order_items_dataset.csv"))
    products    = read_csv_safe(os.path.join(data_path, "olist_products_dataset.csv"))
    payments    = read_csv_safe(os.path.join(data_path, "olist_order_payments_dataset.csv"))
    reviews     = read_csv_safe(os.path.join(data_path, "olist_order_reviews_dataset.csv"))
    sellers     = read_csv_safe(os.path.join(data_path, "olist_sellers_dataset.csv"))
    geolocs     = read_csv_safe(os.path.join(data_path, "olist_geolocation_dataset.csv"))
    translation = read_csv_safe(os.path.join(data_path, "product_category_name_translation.csv"))

    # Prepare unique geolocation by zip prefix
    geolocs_unique = geolocs.drop_duplicates(subset=["geolocation_zip_code_prefix"]) if not geolocs.empty else geolocs

    # Merge geolocation into customers
    if not customers.empty and not geolocs_unique.empty:
        customers = customers.merge(
            geolocs_unique,
            left_on="customer_zip_code_prefix",
            right_on="geolocation_zip_code_prefix",
            how="left",
            suffixes=("", "_geo")
        ).rename(columns={
            "geolocation_lat": "customer_lat",
            "geolocation_lng": "customer_lng",
            "geolocation_city": "customer_geo_city",
            "geolocation_state": "customer_geo_state"
        })

    # Merge geolocation into sellers
    if not sellers.empty and not geolocs_unique.empty:
        sellers = sellers.merge(
            geolocs_unique,
            left_on="seller_zip_code_prefix",
            right_on="geolocation_zip_code_prefix",
            how="left",
            suffixes=("", "_geo")
        ).rename(columns={
            "geolocation_lat": "seller_lat",
            "geolocation_lng": "seller_lng",
            "geolocation_city": "seller_geo_city",
            "geolocation_state": "seller_geo_state"
        })

    # Merge product translations (if available)
    if not products.empty and not translation.empty:
        # translation expected cols: product_category_name, product_category_name_english
        products = products.merge(translation, on="product_category_name", how="left")

    # Merge main tables
    # Use left joins on orders as base
    merged = orders.copy() if not orders.empty else pd.DataFrame()
    if not merged.empty:
        # Stepwise merges; guard for missing tables
        if not customers.empty:
            merged = merged.merge(customers, on="customer_id", how="left")
        if not items.empty:
            merged = merged.merge(items, on="order_id", how="left")
        if not products.empty:
            merged = merged.merge(products, on="product_id", how="left")
        if not payments.empty:
            merged = merged.merge(payments, on="order_id", how="left")
        if not reviews.empty:
            merged = merged.merge(reviews, on="order_id", how="left")
        if not sellers.empty:
            merged = merged.merge(sellers, on="seller_id", how="left")

    # Parse date columns robustly
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date", "shipping_limit_date",
        "review_creation_date", "review_answer_timestamp"
    ]
    for col in date_cols:
        if col in merged.columns:
            merged[col] = pd.to_datetime(merged[col], errors="coerce")

    # Numeric fills for common numeric columns
    for col in ["price", "freight_value", "payment_value"]:
        if col in merged.columns:
            try:
                merged[col] = pd.to_numeric(merged[col], errors="coerce")
                merged[col].fillna(merged[col].median(skipna=True), inplace=True)
            except Exception:
                pass

    # Feature engineering
    if "order_purchase_timestamp" in merged.columns:
        merged["order_year"] = merged["order_purchase_timestamp"].dt.year
        merged["order_month"] = merged["order_purchase_timestamp"].dt.month
    else:
        merged["order_year"] = None
        merged["order_month"] = None

    if "order_delivered_customer_date" in merged.columns and "order_purchase_timestamp" in merged.columns:
        merged["delivery_days"] = (merged["order_delivered_customer_date"] - merged["order_purchase_timestamp"]).dt.days
    else:
        merged["delivery_days"] = None

    # total_order_value: prefer payment_value if available, else price+freight
    if "payment_value" in merged.columns:
        merged["total_order_value"] = merged["payment_value"].fillna(0)
    else:
        merged["total_order_value"] = 0
    if "price" in merged.columns and "freight_value" in merged.columns:
        merged["total_order_value"] = merged["total_order_value"].where(merged["total_order_value"] > 0, merged["price"].fillna(0) + merged["freight_value"].fillna(0))

    # Ensure product dimension columns exist and are numeric
    dim_cols = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    for col in dim_cols:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
        else:
            # create column with NaNs if not present so schema consistent
            merged[col] = pd.NA

    # Keep a broad but reasonable set of columns so queries work
    keep_cols = [
        # order
        "order_id", "order_status", "order_year", "order_month", "order_purchase_timestamp", "shipping_limit_date",
        # customer
        "customer_id", "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix",
        "customer_lat", "customer_lng", "customer_geo_city", "customer_geo_state",
        # seller
        "seller_id", "seller_city", "seller_state", "seller_zip_code_prefix",
        "seller_lat", "seller_lng", "seller_geo_city", "seller_geo_state",
        # product / item
        "order_item_id", "product_id", "product_category_name", "product_category_name_english",
        "product_name_lenght", "product_description_lenght", "product_photos_qty",
        "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm",
        # financial
        "price", "freight_value", "payment_type", "payment_installments", "payment_value", "total_order_value",
        # review
        "review_id", "review_score", "review_creation_date", "review_answer_timestamp",
        "review_comment_title", "review_comment_message",
        # computed
        "delivery_days"
    ]

    # Keep only the intersection to avoid KeyError
    keep_existing = [c for c in keep_cols if c in merged.columns]
    merged = merged[keep_existing].copy()

    print("✅ Final merged shape:", merged.shape)
    return merged
