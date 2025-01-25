from typing import Dict,Union
from pydantic import BaseModel

from model.requests.chat_interface.toggle_chat_interface_setting import UpdateChatInterfaceSettingRequest

class UpdateChatInterfaceSettingsRequest(BaseModel):
    QUERY_SCOPE: Dict[str, Union[UpdateChatInterfaceSettingRequest, bool]]
    SQL_INJECTORS: Dict[str, Union[UpdateChatInterfaceSettingRequest, bool]]
    SQL_GENERATION: Dict[str, Union[UpdateChatInterfaceSettingRequest, bool]]
    