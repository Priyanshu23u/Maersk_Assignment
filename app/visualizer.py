# app/visualizer.py
import plotly.express as px
import pandas as pd
import streamlit as st
import hashlib


def export_pdf_simple(df: pd.DataFrame, filename: str = "analysis_report.pdf"):
    """Export simple PDF summary of DataFrame using fpdf."""
    try:
        from fpdf import FPDF
    except Exception:
        return False, "fpdf not installed"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="E-Commerce Analysis Report", ln=True, align="C")
    pdf.ln(4)
    for col in df.columns[:8]:
        pdf.cell(0, 6, txt=f"{col}: {', '.join(map(str, df[col].dropna().astype(str).head(3)))}", ln=True)
    pdf.output(filename)
    return True, filename


def visualize_result(user_query: str, df: pd.DataFrame):
    """Display result tables, charts, and unique download buttons."""
    if df is None or df.empty:
        st.warning("⚠️ No data found for this query.")
        return

    # Generate a unique hash for widget keys
    unique_key = hashlib.md5(user_query.encode()).hexdigest()[:8]

    # --- Display Data Table ---
    st.dataframe(df.head(100), use_container_width=True)

    # --- Automatic Chart Suggestion ---
    try:
        from google.generativeai import GenerativeModel
        model = GenerativeModel("gemini-2.0-flash")
        chart_prompt = f"""
Based on this query and these columns, suggest the best chart type:
(bar, line, pie, scatter, histogram, or none)
Query: {user_query}
Columns: {list(df.columns)}
"""
        chart_type = model.generate_content(chart_prompt).text.lower().strip()
    except Exception:
        chart_type = "bar"

    if df.shape[1] >= 2:
        x, y = df.columns[0], df.columns[1]
        try:
            if "bar" in chart_type:
                fig = px.bar(df, x=x, y=y, title=f"{y} by {x}")
            elif "line" in chart_type:
                fig = px.line(df, x=x, y=y, title=f"{y} trend")
            elif "pie" in chart_type:
                fig = px.pie(df, names=x, values=y, title=f"{y} share by {x}")
            elif "scatter" in chart_type:
                fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
            else:
                fig = None
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{unique_key}")
        except Exception:
            pass

    # --- Downloads ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        data=csv,
        file_name=f"analysis_result_{unique_key}.csv",
        mime="text/csv",
        key=f"csv_{unique_key}"
    )

    ok, file = export_pdf_simple(df, filename=f"analysis_report_{unique_key}.pdf")
    if ok:
        with open(file, "rb") as f:
            st.download_button(
                "📄 Download PDF",
                data=f,
                file_name=file,
                mime="application/pdf",
                key=f"pdf_{unique_key}"
            )
