# app/chatbot.py
import google.generativeai as genai
from query_executor import QueryExecutor
from visualizer import visualize_result
from utils import clean_sql
import pandas as pd

class ChatBot:
    """
    ChatBot class — converts user questions into SQL using Gemini,
    executes them on DuckDB, and returns a natural language summary + visualization.
    """

    def __init__(self, api_key: str, model_name: str, df: pd.DataFrame):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.executor = QueryExecutor(df)
        self.df = df

    def _generate_schema_description(self) -> str:
        """
        Builds a dynamic schema description string including product dimensions.
        """
        cols = list(self.df.columns)
        schema_description = (
            f"This dataset has {len(cols)} columns: {', '.join(cols)}.\n"
            "Rows correspond to e-commerce order items. Key column meanings:\n"
            "- 'product_category_name' → Portuguese product category name\n"
            "- 'product_category_name_english' → English translation of category\n"
            "- 'product_length_cm', 'product_height_cm', 'product_width_cm' → product dimensions (cm)\n"
            "- 'product_weight_g' → product weight (grams)\n"
            "- 'price', 'payment_value', 'freight_value' → financial columns (BRL)\n"
            "- 'delivery_days' → days between purchase and delivery\n"
            "- 'review_score' → rating (1-5)\n"
            "- 'customer_state', 'customer_geo_state', 'seller_geo_state' → geography\n"
            "Use these exact column names when generating SQL queries."
        )
        return schema_description

    def ask(self, user_query: str):
        """
        Convert user_query -> SQL (via Gemini), execute, summarize result, visualize and return English summary.
        """
        try:
            schema_context = self._generate_schema_description()
            prompt_sql = f"""
You are an expert data analyst with access to a DuckDB table named 'olist'.
{schema_context}

Task:
- Convert the user's question into a valid DuckDB SQL query that runs on table 'olist'.
- Use column names exactly as provided.
- If the user asks for translation of a product category, map between product_category_name and product_category_name_english.
- If user asks for a metric related to dimensions (width/height/length/weight), use product_width_cm/product_height_cm/product_length_cm/product_weight_g respectively.
- Return ONLY the SQL query (no markdown, no explanation).

User Question: "{user_query}"
"""
            response_sql = self.model.generate_content(prompt_sql)
            sql_query = clean_sql(response_sql.text)

            # Run the SQL
            result = self.executor.run_query(sql_query)
            if isinstance(result, str):  # error string
                # attempt automatic fix
                fixed = self._attempt_sql_fix(user_query, result)
                if fixed:
                    result = self.executor.run_query(fixed)
                    if isinstance(result, str):
                        # still error
                        return fixed  # return the suggested fixed query or error
                    sql_query = fixed
                else:
                    return result

            # Ask Gemini to summarize the result in natural English
            summary_prompt = f"""
You are an expert business analyst. Produce a short (2-4 sentence) manager-friendly summary of the query result.

Original question: {user_query}
SQL used: {sql_query}

First few rows of the result (for context):
{result.head(10).to_markdown()}
"""
            response_summary = self.model.generate_content(summary_prompt)
            summary_text = response_summary.text.strip()

            # Visualize result (Streamlit)
            visualize_result(user_query, result)

            # Return summary string (UI will display it)
            return f"🗣️ **Answer:** {summary_text}"

        except Exception as e:
            return f"❌ Error: {e}"

    def _attempt_sql_fix(self, user_query: str, error_message: str):
        """
        When SQL execution fails, ask the LLM to propose a corrected SQL query.
        """
        try:
            correction_prompt = f"""
A SQL query executed on DuckDB failed with the following error:
{error_message}

User question: {user_query}

Using the same schema and logic, provide a corrected SQL query that would run on table 'olist'.
Return only the corrected SQL query (no markdown).
"""
            correction = self.model.generate_content(correction_prompt)
            fixed_sql = clean_sql(correction.text)
            print("🛠️ Auto-corrected SQL suggestion:", fixed_sql)
            return fixed_sql
        except Exception:
            return None
