import duckdb
import pandas as pd

class QueryExecutor:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.conn = duckdb.connect(database=":memory:")
        self.conn.register("olist", self.df)

    def run_query(self, sql_query: str):
        try:
            print(f"🧠 Executing query:\n{sql_query}")
            result = self.conn.execute(sql_query).fetchdf()
            return result
        except Exception as e:
            return f"❌ Query error: {e}"
