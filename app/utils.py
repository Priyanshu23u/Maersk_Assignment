def clean_sql(sql: str) -> str:
    """Cleans model-generated SQL text for safe execution."""
    sql = sql.replace("```sql", "").replace("```", "")
    sql = sql.replace(";", "")
    return sql.strip()
