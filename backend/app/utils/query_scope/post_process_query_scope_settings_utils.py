from model.query_scope.query_scope import QueryScope

class PostProcessQueryScopeSettingsUtils:
    @staticmethod
    def ensure_wildcards_for_tables(query_scope: QueryScope) -> QueryScope:
        """
        Ensures that each table in `tables` has a corresponding `table.*` in `columns`
        if explicit columns for that table are not already present.
        """
        tables = query_scope.entities.tables
        columns = set(query_scope.entities.columns)

        for table in tables:
            if not any(col.startswith(f"{table}.") for col in columns):
                columns.add(f"{table}.*")

        query_scope.entities.columns = list(columns)
        return query_scope
