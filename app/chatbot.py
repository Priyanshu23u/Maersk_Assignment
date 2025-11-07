import google.generativeai as genai
from app.query_executor import QueryExecutor
from app.visualizer import visualize_result
from app.utils import clean_sql

class ChatBot:
    def __init__(self, api_key: str, model_name: str, df):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.executor = QueryExecutor(df)

    def ask(self, user_query: str):
        prompt = f"""
        You are an expert data analyst with access to a DuckDB table named 'olist'.
        The columns include:
        order_id, customer_state, customer_city, customer_lat, customer_lng,
        seller_lat, seller_lng, product_category_name_english,
        price, payment_value, review_score, order_year, order_month,
        delivery_days, total_order_value, etc.

        Convert this user question into a valid SQL query for DuckDB.
        Use only the above column names.
        Return ONLY the SQL query — no text or markdown.

        User Query: "{user_query}"
        """

        try:
            response = self.model.generate_content(prompt)
            sql_query = clean_sql(response.text)
            result = self.executor.run_query(sql_query)
            if isinstance(result, str):
                return result
            return visualize_result(user_query, result)
        except Exception as e:
            return f"❌ Error: {e}"
