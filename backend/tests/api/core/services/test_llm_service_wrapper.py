import pytest
import json
from unittest import mock
from fastapi import HTTPException
from api.core.services.llm_wrapper.llm_service_wrapper import LLMServiceWrapper
from utils.llm_wrapper.sql_generation_output_utils import SQLUtils
from model.query_scope.query_scope import QueryScope
from model.requests.sql_generation.user_input_request import UserInputRequest

@pytest.mark.asyncio
class TestLLMServiceWrapper:

    def init_mock_user_input(self, query: str) -> UserInputRequest:
        return UserInputRequest(input=query)

    def init_mock_resolved_schema(self) -> dict:
        return {
            "tables": {
                "orders": {
                    "synonyms": ["purchases", "transactions"],
                    "columns": {
                        "order_id": {"type": "INTEGER"},
                        "customer_id": {"type": "INTEGER"},
                        "order_date": {"type": "DATE"}
                    },
                    "relationships": {
                        "customers": {
                            "table": "customers",
                            "on": "orders.customer_id = customers.customer_id",
                            "type": "INNER"
                        }
                    }
                }
            }
        }

    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_get_query_scope_using_default_mode_success(self, mock_openai):
        # Arrange
        user_input = self.init_mock_user_input("Fetch orders and customer details")

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content=json.dumps({
            "intent": "fetch_data",
            "entities": {
                "tables": ["orders", "customers"],
                "columns": ["orders.order_id", "customers.customer_id"]
            }
        })))]
        mock_response.usage = mock.Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_client.chat.completions.create.return_value = mock_response

        # Act
        query_scope = await LLMServiceWrapper.get_query_scope_using_default_mode(user_input)

        # Assert
        assert query_scope.intent == "fetch_data"
        assert query_scope.entities.tables == ["orders", "customers"]
        assert query_scope.entities.columns == ["orders.order_id", "customers.customer_id"]
        mock_client.chat.completions.create.assert_called_once()

    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_get_query_scope_invalid_response(self, mock_openai):
        # Arrange
        user_input = self.init_mock_user_input("Invalid query")

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content="{invalid: json}"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await LLMServiceWrapper.get_query_scope_using_default_mode(user_input)

        # Assert
        assert exc_info.value.status_code == 500
        assert "Failed to generate structured query scope" in str(exc_info.value.detail)


    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_generate_sql_query_success(self, mock_openai):
        # Arrange
        user_input = self.init_mock_user_input("Get order_id and order_date from orders")
        resolved_schema = self.init_mock_resolved_schema()

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content="SELECT order_id, order_date FROM orders;"))]
        mock_response.usage = mock.Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_client.chat.completions.create.return_value = mock_response

        # Act
        generated_sql = await LLMServiceWrapper.generate_sql_query(user_input, resolved_schema)

        # Assert
        assert generated_sql == "SELECT order_id, order_date FROM orders;"
        mock_client.chat.completions.create.assert_called_once()

    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_generate_sql_query_invalid_response(self, mock_openai):
        # Arrange
        user_input = self.init_mock_user_input("Invalid SQL query")
        resolved_schema = self.init_mock_resolved_schema()

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content="invalid sql response"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await LLMServiceWrapper.generate_sql_query(user_input, resolved_schema)

        # Assert
        assert exc_info.value.status_code == 500
        assert "Failed to generate SQL query" in str(exc_info.value.detail)
