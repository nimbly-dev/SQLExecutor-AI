from typing import List, Dict, Union

def expand_columns(query_columns: set, schema_tables: set, schema_columns: Dict[str, List[str]]) -> set:
    """
    Expands wildcard columns (e.g., "orders.*") into individual column names from the schema.
    """

    # Filter and validate base columns
    base_columns = {
        col for col in query_columns if not col.endswith(".*") and _validate_column(col, schema_columns)
    }

    # Expand wildcard columns
    expanded_columns = {
        f"{table}.{column}"
        for wildcard in query_columns if wildcard.endswith(".*")
        for table in {wildcard.split(".*")[0]} if table in schema_tables
        for column in schema_columns.get(table, [])
    }

    # Combine base columns and expanded columns
    result = base_columns.union(expanded_columns)

    return result

def _validate_column(column: str, schema_columns: Dict[str, List[str]]) -> bool:
    """
    Validates if a column exists in the schema.
    Args:
        column (str): Column in the format 'table.column'.
        schema_columns (dict): Mapping of table names to their columns.

    Returns:
        bool: True if column exists in the schema, False otherwise.
    """
    if "." not in column:
        return False
    table, col = column.split(".", 1)
    return col in schema_columns.get(table, [])
