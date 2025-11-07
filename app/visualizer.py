import plotly.express as px
import pandas as pd
import streamlit as st

def visualize_result(user_query, df: pd.DataFrame):
    st.write(f"### 💡 Query: {user_query}")
    st.dataframe(df.head())

    if df.shape[1] == 2 and df.select_dtypes(include='number').shape[1] == 1:
        chart = px.bar(df, x=df.columns[0], y=df.columns[1], title="Result Chart")
        st.plotly_chart(chart)
    else:
        st.write("📊 No chart generated for this result type.")

    return "✅ Query executed successfully!"
