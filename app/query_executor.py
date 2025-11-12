# app/query_executor.py
import duckdb
import pandas as pd

class QueryExecutor:
    """
    Registers a pandas DataFrame in an in-memory DuckDB instance and
    executes SQL queries safely.
    """
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self.conn = duckdb.connect(database=":memory:")
        # register table name 'olist'
        self.conn.register("olist", self.df)

    def run_query(self, sql_query: str):
        try:
            print(f"🧠 Executing SQL:\n{sql_query}")
            result = self.conn.execute(sql_query).fetchdf()
            return result
        except Exception as e:
            return f"❌ Query error: {e}"
