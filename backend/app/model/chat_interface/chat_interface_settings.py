from typing import Dict
from pydantic import BaseModel

from model.chat_interface.chat_interface_setting import ChatInterfaceSetting

class ChatInterfaceSettings(BaseModel):
    query_scope_setting: Dict[str, Dict[str, ChatInterfaceSetting]]
    injectors_setting: Dict[str, Dict[str, ChatInterfaceSetting]]
    sql_generation: Dict[str, Dict[str, ChatInterfaceSetting]]