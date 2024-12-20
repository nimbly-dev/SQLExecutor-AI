import pytest
import logging
from unittest import mock
from fastapi import HTTPException
from utils.ruleset.ruleset_utils import resolve_field
from utils.ruleset.ruleset_condition_utils import format_value, normalize_condition
from api.core.services.ruleset.ruleset_conditions_service import RulesetConditionsService


class TestRulesetConditionsService:

    @pytest.mark.skip(reason="SQLEXEC-32: Skipping temporarily as this UT is complex and takes much time")
    @mock.patch("utils.ruleset.ruleset_utils.resolve_field")
    @mock.patch("utils.ruleset.ruleset_condition_utils.format_value")
    @mock.patch("utils.ruleset.ruleset_condition_utils.normalize_condition")
    def test_evaluate_condition_success(self, mock_normalize_condition, mock_format_value, mock_resolve_field):
        # Arrange
        condition = "${jwt.custom_fields.active} == True"
        session_data = {"custom_fields": {"active": True}}
        mock_resolve_field.side_effect = lambda data, path: data.get("custom_fields", {}).get("active")
        mock_format_value.side_effect = lambda value: "True" if value is True else "None"
        mock_normalize_condition.side_effect = lambda x: x

        # Act
        result = RulesetConditionsService.evaluate_condition(condition, session_data)

        # Assert
        assert result is True
        mock_resolve_field.assert_called_once_with(session_data, "jwt.custom_fields.active")
        mock_format_value.assert_called_once_with(True)

    @pytest.mark.skip(reason="SQLEXEC-32: Skipping temporarily as this UT is complex and takes much time")
    @mock.patch("utils.ruleset.ruleset_utils.resolve_field")
    @mock.patch("utils.ruleset.ruleset_condition_utils.format_value")
    def test_evaluate_condition_field_not_found(self, mock_format_value, mock_resolve_field):
        # Arrange
        condition = "${jwt.custom_fields.nonexistent} == True"
        session_data = {"custom_fields": {"active": True}}
        mock_resolve_field.return_value = None
        mock_format_value.side_effect = lambda value: "None" if value is None else "True"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            RulesetConditionsService.evaluate_condition(condition, session_data)

        assert exc_info.value.status_code == 400
        assert "Field 'custom_fields.nonexistent' is not found in session data" in str(exc_info.value.detail)

    @mock.patch("utils.ruleset.ruleset_utils.resolve_field")
    @mock.patch("utils.ruleset.ruleset_condition_utils.normalize_condition")
    def test_evaluate_condition_invalid_syntax(self, mock_normalize_condition, mock_resolve_field):
        # Arrange
        condition = "${jwt.custom_fields.active} == True &&"
        session_data = {"custom_fields": {"active": True}}
        mock_resolve_field.side_effect = lambda data, path: data["custom_fields"]["active"]
        mock_normalize_condition.side_effect = lambda x: x

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            RulesetConditionsService.evaluate_condition(condition, session_data)

        assert exc_info.value.status_code == 400
        assert "Invalid condition" in str(exc_info.value.detail)

    @mock.patch("utils.ruleset.ruleset_utils.resolve_field")
    def test_resolve_condition_named_conditions(self, mock_resolve_field):
        # Arrange
        condition = "${conditions.is_active_user}"
        session_data = {"custom_fields": {"active": True}}
        conditions_dict = {"is_active_user": "${jwt.custom_fields.active} == True"}
        mock_resolve_field.side_effect = lambda data, path: data["custom_fields"]["active"]

        # Act
        resolved_condition = RulesetConditionsService.resolve_condition(condition, session_data, conditions_dict)

        # Assert
        assert resolved_condition == "True == True"

    @mock.patch("utils.ruleset.ruleset_utils.resolve_field")
    @mock.patch("utils.ruleset.ruleset_condition_utils.format_value")
    def test_resolve_condition_jwt_placeholders(self, mock_format_value, mock_resolve_field):
        # Arrange
        condition = "${jwt.custom_fields.active} == True"
        session_data = {"custom_fields": {"active": True}}
        mock_resolve_field.side_effect = lambda data, path: data["custom_fields"]["active"]
        mock_format_value.side_effect = lambda value: "True" if value is True else "None"

        # Act
        resolved_condition = RulesetConditionsService.resolve_condition(condition, session_data, None)

        # Assert
        assert resolved_condition == "True == True"

    @mock.patch("utils.ruleset.ruleset_utils.resolve_field")
    def test_resolve_condition_undefined_named_condition(self, mock_resolve_field):
        # Arrange
        condition = "${conditions.is_active_user}"
        session_data = {"custom_fields": {"active": True}}
        conditions_dict = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            RulesetConditionsService.resolve_condition(condition, session_data, conditions_dict)

        assert exc_info.value.status_code == 400
        assert "Condition 'is_active_user' is not defined" in str(exc_info.value.detail)

    @pytest.mark.skip(reason="SQLEXEC-32: Skipping temporarily as this UT is complex and takes much time")
    def test_merge_column_access(self):
        # Arrange
        global_rule = mock.Mock(columns=mock.Mock(allow=["id", "name"], deny=["password"]))
        group_rule_columns = mock.Mock(allow=["email"], deny=["name"])
        user_rule = mock.Mock(columns=mock.Mock(allow=["*"], deny=["password"]))
        table_schema = mock.Mock(columns={"id": None, "name": None, "email": None, "password": None})

        # Act
        allowed_columns, denied_columns = RulesetConditionsService.merge_column_access(
            global_rule, group_rule_columns, user_rule, table_schema
        )

        # Assert
        assert allowed_columns == {"id", "email"}
        assert denied_columns == {"password", "name"}

    @pytest.mark.skip(reason="SQLEXEC-32: Skipping temporarily as this UT is complex and takes much time")
    def test_merge_column_access_no_user_rule(self):
        # Arrange
        global_rule = mock.Mock(columns=mock.Mock(allow=["id"], deny=["password"]))
        group_rule_columns = mock.Mock(allow=["email"], deny=["*"])
        user_rule = None
        table_schema = mock.Mock(columns={"id": None, "name": None, "email": None, "password": None})

        # Act
        allowed_columns, denied_columns = RulesetConditionsService.merge_column_access(
            global_rule, group_rule_columns, user_rule, table_schema
        )

        # Assert
        assert allowed_columns == {"id"}
        assert denied_columns == {"password", "name", "email"}

    def test_resolve_table_references(self):
        # Arrange
        condition = "customers.customer_id == orders.customer_id"
        session_data = {"customers": {"customer_id": 123}, "orders": {"customer_id": 123}}

        # Act
        resolved_condition = RulesetConditionsService._resolve_table_references(condition, session_data)

        # Assert
        assert resolved_condition == "None == None"

    def test_resolve_table_references_with_unmatched_fields(self):
        # Arrange
        condition = "customers.customer_id == orders.nonexistent_id"
        session_data = {"customers": {"customer_id": 123}, "orders": {}}

        # Act
        resolved_condition = RulesetConditionsService._resolve_table_references(condition, session_data)

        # Assert
        assert resolved_condition == "None == None"
