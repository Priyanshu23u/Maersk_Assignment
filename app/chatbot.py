import google.generativeai as genai
from app.query_executor import QueryExecutor
from app.visualizer import visualize_result
import textwrap

class ChatBot:
    def __init__(self, api_key, model_name, df):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.executor = QueryExecutor(df)

    def ask(self, user_query):
        prompt = f"""
        You are a data analyst working on an e-commerce dataset named 'olist'.
        Convert this user query into a valid SQL query for DuckDB.
        Return ONLY the SQL query, nothing else.

        User Query: "{user_query}"
        """
        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip().strip('`')
            result = self.executor.run_query(sql_query)
            if isinstance(result, str):
                return result
            return visualize_result(user_query, result)
        except Exception as e:
            return f"❌ Error: {e}"
