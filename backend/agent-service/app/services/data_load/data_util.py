import re

def is_iso_date(s: str) -> bool:
    """YYYY-MM-DD 형식인지 간단히 체크"""
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s))