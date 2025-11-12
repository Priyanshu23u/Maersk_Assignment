# app/chatbot.py
import google.generativeai as genai
from query_executor import QueryExecutor
from utils import clean_sql
import pandas as pd
from collections import deque

class ChatBot:
    """Conversational AI Assistant — generates SQL, executes, summarizes, and returns both text + dataframe."""

    def __init__(self, api_key: str, model_name: str, df: pd.DataFrame):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.executor = QueryExecutor(df)
        self.df = df
        self.memory = deque(maxlen=6)

    def _generate_schema_description(self) -> str:
        cols = list(self.df.columns)
        return (
            f"The dataset has {len(cols)} columns: {', '.join(cols)}.\n"
            "Use 'olist' as the table name. Important columns:\n"
            "- product_category_name / product_category_name_english → category names\n"
            "- product_length_cm, product_height_cm, product_width_cm, product_weight_g → dimensions\n"
            "- price, payment_value, freight_value → financial metrics\n"
            "- delivery_days → delivery time (days)\n"
            "- review_score → 1–5 rating\n"
            "- customer_state, seller_geo_state → geography\n"
        )

    def _get_memory_context(self) -> str:
        if not self.memory:
            return "No previous conversation."
        return "\n".join([f"User: {q}\nBot: {a}" for q, a in self.memory])

    def ask(self, user_query: str):
        """Processes a user query, runs SQL if needed, returns dict: {answer, result}"""
        try:
            user_query = user_query.strip()
            if not user_query:
                return {"answer": "⚠️ Please provide a question.", "result": None}

            # Glossary / Definition Mode
            if any(k in user_query.lower() for k in ["what is", "define", "meaning of", "explain correlation between"]):
                glossary_prompt = f"""
You are an analytics tutor. Explain this concept clearly in 3–4 lines in context of e-commerce analytics.
Query: {user_query}
"""
                glossary = self.model.generate_content(glossary_prompt).text.strip()
                self.memory.append((user_query, glossary))
                return {"answer": f"📘 **Definition:** {glossary}", "result": None}

            # Language Translation
            translation_prompt = f"""
Translate this query into English if needed; else return it unchanged:
Query: "{user_query}"
"""
            translated = self.model.generate_content(translation_prompt).text.strip()
            user_query_en = translated or user_query

            # SQL Generation
            schema = self._generate_schema_description()
            memory = self._get_memory_context()
            prompt_sql = f"""
You are a data analyst working with DuckDB (table name: olist).
{schema}

Conversation so far:
{memory}

User query: "{user_query_en}"

Generate a valid DuckDB SQL query (no markdown, no explanation).
"""
            response_sql = self.model.generate_content(prompt_sql)
            sql_query = clean_sql(response_sql.text)
            if not sql_query:
                return {"answer": "⚠️ Unable to create SQL for this query.", "result": None}

            # SQL Execution
            result = self.executor.run_query(sql_query)
            if isinstance(result, str):
                fix = self._attempt_sql_fix(user_query_en, result)
                if fix:
                    result = self.executor.run_query(fix)
                    if isinstance(result, str):
                        return {"answer": result, "result": None}
                    sql_query = fix
                else:
                    return {"answer": result, "result": None}

            # Summarize
            summary_prompt = f"""
Write a concise 3–4 sentence summary explaining these results for a manager.

User question: {user_query_en}
SQL: {sql_query}

Sample data:
{result.head(10).to_markdown()}
"""
            summary = self.model.generate_content(summary_prompt).text.strip()
            self.memory.append((user_query_en, summary))

            return {"answer": f"🗣️ **Answer:** {summary}", "result": result}

        except Exception as e:
            return {"answer": f"❌ Error: {e}", "result": None}

    def _attempt_sql_fix(self, user_query: str, error_msg: str):
        """Try to fix invalid SQL automatically."""
        try:
            prompt_fix = f"""
A DuckDB SQL query failed with error: {error_msg}
User query: {user_query}
Generate a corrected SQL query (no markdown).
"""
            fix = self.model.generate_content(prompt_fix).text.strip()
            return clean_sql(fix)
        except Exception:
            return None
