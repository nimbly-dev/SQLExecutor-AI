import re

def format_value(value):
    """
    Format values for substitution in the condition string.
    """
    if isinstance(value, list):
        return f"[{', '.join(repr(v) for v in value)}]"
    elif isinstance(value, bool):
        return "True" if value else "False"
    elif value is None:
        return "None"
    else:
        return repr(value) 

def normalize_condition(condition: str) -> str:
    """
    Normalize the condition string:
    - Convert logical operators to lowercase.
    - Replace `TRUE` with `True` and `FALSE` with `False`.
    """
    condition = re.sub(r'\bIN\b', 'in', condition)
    condition = re.sub(r'\bOR\b', 'or', condition)
    condition = re.sub(r'\bAND\b', 'and', condition)
    condition = re.sub(r'\bTRUE\b', 'True', condition, flags=re.IGNORECASE)
    condition = re.sub(r'\bFALSE\b', 'False', condition, flags=re.IGNORECASE)
    return condition
