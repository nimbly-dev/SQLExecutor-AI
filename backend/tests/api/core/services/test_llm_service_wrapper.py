import pytest
import json
from unittest import mock
from fastapi import HTTPException
from api.core.services.llm_wrapper.llm_service_wrapper import LLMServiceWrapper
from utils.prompt_instructions_utils import DefaultPromptInstructionsUtil
from model.query_scope import QueryScope
from model.query_scope.entities import Entities
from pydantic import ValidationError

@pytest.mark.asyncio
class TestLLMServiceWrapper:
    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_get_query_scope_using_default_mode_success(self, mock_openai):
        # Arrange
        user_input = mock.Mock()
        user_input.input = "Show me customer details and order information"

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content=json.dumps({
            "intent": "fetch_data",
            "entities": {
                "tables": ["customers", "orders"],
                "columns": ["customers.customer_name", "orders.order_id"]
            }
        })))]
        mock_response.usage = mock.Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_client.chat.completions.create.return_value = mock_response

        # Act
        query_scope = await LLMServiceWrapper.get_query_scope_using_default_mode(user_input)

        # Assert
        assert query_scope.intent == "fetch_data"
        assert query_scope.entities.tables == ["customers", "orders"]
        assert query_scope.entities.columns == ["customers.customer_name", "orders.order_id"]
        mock_client.chat.completions.create.assert_called_once()

    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_get_query_scope_using_default_mode_invalid_response(self, mock_openai):
        # Arrange
        user_input = mock.Mock()
        user_input.input = "Invalid query"

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        # Simulate an invalid JSON response
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content="{invalid: json}"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            await LLMServiceWrapper.get_query_scope_using_default_mode(user_input)

    @mock.patch("api.core.services.llm_wrapper.llm_service_wrapper.OpenAI")
    async def test_get_query_scope_using_default_mode_invalid_response(self, mock_openai):
        # Arrange
        user_input = mock.Mock()
        user_input.input = "Invalid query"

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        # Simulate an invalid JSON response
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
    async def test_get_query_scope_using_default_mode_validation_error(self, mock_openai):
        # Arrange
        user_input = mock.Mock()
        user_input.input = "Query causing validation error"

        mock_client = mock.Mock()
        mock_openai.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content=json.dumps({
            "intent": "fetch_data",
            "entities": {
                "tables": "customers", 
                "columns": ["customers.customer_name", "orders.order_id"]
            }
        })))]
        mock_client.chat.completions.create.return_value = mock_response

        # Act 
        with pytest.raises(HTTPException) as exc_info:
            await LLMServiceWrapper.get_query_scope_using_default_mode(user_input)

        # Assert that the exception is properly raised
        assert exc_info.value.status_code == 500
        assert "Failed to generate structured query scope" in str(exc_info.value.detail)
