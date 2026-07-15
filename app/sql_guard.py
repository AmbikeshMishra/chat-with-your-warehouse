import re

_BLOCKED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|MERGE|REPLACE"
    r"|GRANT|REVOKE|EXEC|EXECUTE|CALL|COPY|PUT|GET|REMOVE|UNDROP)\b",
    re.IGNORECASE,
)


def is_safe_sql(sql: str) -> bool:
    return not bool(_BLOCKED.search(sql))
