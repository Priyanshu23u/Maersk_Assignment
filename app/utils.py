# app/utils.py
def clean_sql(sql: str) -> str:
    """Cleans model-generated SQL text for safe execution."""
    if not isinstance(sql, str):
        return ""
    # remove markdown fences and code blocks
    sql = sql.replace("```sql", "").replace("```", "")
    # remove common backticks
    sql = sql.replace("`", "")
    # remove trailing semicolons to avoid multi-statement issues
    sql = sql.strip()
    if sql.endswith(";"):
        sql = sql[:-1]
    return sql.strip()
