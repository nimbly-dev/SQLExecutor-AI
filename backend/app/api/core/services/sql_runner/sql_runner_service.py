from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from model.query_scope.query_scope import QueryScope
from model.responses.sql_generation.sql_generation_error import ErrorType, SqlRunErrorResponse
from model.tenant.tenant import Tenant

from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import EXTERNAL_SYSTEM_DB_SETTING
from utils.external_system_utils.external_system_db_utils import build_db_url_based_on_dialect

class SqlRunnerService:
    
    @staticmethod
    def run_sql(query: str, tenant: Tenant, 
                orginal_user_input: str = None, 
                query_scope: QueryScope = None, 
                schema_name: str = None,
                params: dict = None):
        sql_flavor = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_DB_SETTING,
            setting_key="EXTERNAL_TENANT_DB_DIALECT"
        )

        if sql_flavor not in ["postgresql", "mysql", "sqlite"]:
            raise ValueError(f"Unsupported SQL flavor: {sql_flavor}")
        
        db_connection_url = build_db_url_based_on_dialect(tenant, sql_flavor, schema=schema_name)

        # Conditionally exclude pool settings for SQLite:
        if "sqlite" in db_connection_url.lower():
            engine = create_engine(db_connection_url)
        else:
            engine = create_engine(db_connection_url, pool_size=10, max_overflow=20)


        try:
            with engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            if query_scope is not None and orginal_user_input is not None:
                error_response = SqlRunErrorResponse(
                    error_type=ErrorType.RUNTIME_ERROR,
                    message="An error occurred while executing the query.",
                    user_query_scope=query_scope,
                    user_input=orginal_user_input,
                    sql_query=query,
                    error_message=e._message()
                )
                raise HTTPException(
                    status_code=400,
                    detail=error_response.dict()  
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"An error occurred while executing the query: {str(e)}"
                )
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
        finally:
            engine.dispose()