from pydantic import BaseModel, Field, root_validator
from typing import Dict

from model.column_rule import ColumnRule

class UserSpecificTableRule(BaseModel):
    columns: ColumnRule