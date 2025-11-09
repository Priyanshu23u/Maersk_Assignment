# app/utils.py
def clean_sql(sql: str) -> str:
    """Cleans model-generated SQL text for safe execution."""
    if not isinstance(sql, str):
        return ""
    sql = sql.replace("```sql", "").replace("```", "")
    # remove common code fences / markdown
    sql = sql.strip()
    # remove trailing semicolons to avoid multi-statement issues
    if sql.endswith(";"):
        sql = sql[:-1]
    return sql.strip()
