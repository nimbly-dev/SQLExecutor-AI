# import pytest
# import json

# from unittest import mock
# from unittest.mock import AsyncMock

# from model.query_scope import QueryScope
# from model.entities import Entities
# from model.schema import Schema

# from tests.testing_utilities.test_utils import RESOURCES_PATH
# from utils.query_scope.post_process_query_scope_settings_utils import PostProcessQueryScopeSettingsUtils


# class TestPostProcessQueryScopeSettingsUtils:
    
#     def test_remove_missing_columns_from_query_scope(self):
#         # Arrange
#         with open(f'{RESOURCES_PATH}/schemas/valid/two_tables_with_relationships.json', 'r') as schema_file:
#             schema_data = json.load(schema_file)

#         schema_data["tenant_id"] = "tenant_123"
#         schema_instance = Schema(**schema_data)

#         query_scope_data = {
#             "intent": "fetch_data",
#             "entities": {
#                 "tables": ["customers", "orders"],
#                 "columns": [
#                     "customers.name",  
#                     "orders.amount",
#                     "orders.nonexistent_column",
#                     "nonexistent_table.nonexistent_column",
#                     "*"
#                 ]
#             }
#         }
#         query_scope = QueryScope(**query_scope_data)

#         # Act
#         updated_query_scope = PostProcessQueryScopeSettingsUtils.remove_missing_columns_from_query_scope(
#             schema=schema_instance,
#             query_scope=query_scope
#         )


#         # Assert
#         assert updated_query_scope.entities.tables == ["customers", "orders"]
#         assert "*" in updated_query_scope.entities.columns
#         assert "customers.name" in updated_query_scope.entities.columns
#         assert "orders.amount" in updated_query_scope.entities.columns
#         assert "orders.nonexistent_column" not in updated_query_scope.entities.columns
#         assert "nonexistent_table.nonexistent_column" not in updated_query_scope.entities.columns
