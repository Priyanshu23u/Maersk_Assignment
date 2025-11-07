import plotly.express as px
import pandas as pd
import streamlit as st

def visualize_result(user_query: str, df: pd.DataFrame):
    st.write(f"### 💬 Query: {user_query}")
    st.dataframe(df.head())

    if df.empty:
        st.warning("⚠️ No results found for this query.")
        return "No data returned."

    # 2-column numeric (bar chart)
    if df.shape[1] == 2 and df.select_dtypes(include='number').shape[1] == 1:
        chart = px.bar(df, x=df.columns[0], y=df.columns[1], title="📊 Result Visualization")
        st.plotly_chart(chart, use_container_width=True)

    # 2 numeric columns (scatter)
    elif df.shape[1] == 2 and df.select_dtypes(include='number').shape[1] == 2:
        chart = px.scatter(df, x=df.columns[0], y=df.columns[1], title="📈 Scatter Plot")
        st.plotly_chart(chart, use_container_width=True)

    # 3 or more columns (show table)
    else:
        st.info("📄 Showing data table only.")

    return "✅ Query executed successfully!"
