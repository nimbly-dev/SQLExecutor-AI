# The quickest fix is to ensure that when you're testing SQLite, you don't pass
# the 'pool_size' or 'max_overflow' args. One way is to conditionally create the
# engine within your SqlRunnerService based on whether the DB URL is SQLite.

# Example service code fix (no changes needed in the tests):

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from model.tenant.tenant import Tenant
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import SQL_RUNNER

class SqlRunnerService:
    
    @staticmethod
    def run_sql(query: str, tenant: Tenant, params: dict = None):
        sql_flavor = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_RUNNER,
            setting_key="SQL_FLAVOR"
        )

        db_connection_url = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_RUNNER,
            setting_key="EXTERNAL_SYSTEM_DB_CONNECTION_URL"
        )

        if sql_flavor not in ["postgres", "mysql", "sqlite"]:
            raise ValueError(f"Unsupported SQL flavor: {sql_flavor}")

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
            return f"Query execution failed: {str(e)}"
        finally:
            engine.dispose()
