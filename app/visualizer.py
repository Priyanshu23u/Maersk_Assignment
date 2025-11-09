# app/visualizer.py
import plotly.express as px
import pandas as pd
import streamlit as st

def visualize_result(user_query: str, df: pd.DataFrame):
    """
    Display the query and an appropriate visualization / result in Streamlit.
    Handles empty DataFrames, single-value numeric results, and multi-column results.
    """
    st.markdown(f"### 💬 **Query:** {user_query}")

    if df is None or (hasattr(df, "empty") and df.empty):
        st.warning("⚠️ No matching data found for this query.")
        st.info("However, the assistant may provide an English explanation below.")
        return None

    # If single cell or single column with a single row numeric result, show it prominently
    # e.g., SELECT MAX(product_width_cm) ...
    if df.shape[0] == 1 and df.shape[1] == 1 and pd.api.types.is_numeric_dtype(df.dtypes[0]):
        val = df.iloc[0, 0]
        col = df.columns[0]
        st.success(f"✅ Result: **{col} = {val}**")
        return "single_value"

    # If single column with numbers, show top / histogram / table
    if df.shape[1] == 1 and pd.api.types.is_numeric_dtype(df.iloc[:,0].dtype):
        st.dataframe(df.head(50), use_container_width=True)
        try:
            fig = px.histogram(df, x=df.columns[0], nbins=30, title=f"Distribution of {df.columns[0]}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass
        return "one_column"

    # If two columns and one numeric, show bar chart
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if df.shape[1] == 2 and len(numeric_cols) >= 1:
        # assume first non-numeric is x, numeric is y
        x_col = df.columns[0] if not pd.api.types.is_numeric_dtype(df[df.columns[0]].dtype) else df.columns[1]
        y_col = numeric_cols[0]
        st.dataframe(df.head(50), use_container_width=True)
        try:
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass
        return "two_column"

    # For other cases show a table and small guidance
    st.dataframe(df.head(50), use_container_width=True)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) > 0:
        st.info("📄 Numeric columns detected — results shown in the table above.")
    else:
        st.info("ℹ️ This query returned text-based results (e.g., translations or labels).")
    return "table"
