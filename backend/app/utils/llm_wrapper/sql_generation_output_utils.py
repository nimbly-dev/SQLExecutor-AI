
class SQLUtils:
    
    @staticmethod
    def normalize_sql(generated_sql: str) -> str:
        """
        Normalizes the SQL query by removing markdown formatting, extra spaces, and newlines.

        Args:
            generated_sql (str): The SQL query string.

        Returns:
            str: The normalized SQL query.
        """
        # Remove Markdown formatting
        if generated_sql.startswith("```sql"):
            generated_sql = generated_sql.strip("```sql").strip().strip("```")

        # Replace newlines and normalize multiple spaces to a single space
        generated_sql = " ".join(generated_sql.splitlines())
        generated_sql = " ".join(generated_sql.split())
        return generated_sql