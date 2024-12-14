from fastapi import APIRouter, Depends

from api.core.services.llm_wrapper.llm_service_wrapper import LLMServiceWrapper
from model.requests.sql_generation.user_input_request import UserInputRequest

from utils.jwt_utils import authenticate_session

router = APIRouter()

@router.post("/{tenant_id}")
async def generate_sql(tenant_id: str,user_request: UserInputRequest, session: dict = Depends(authenticate_session)):
    user_query_scope = await LLMServiceWrapper.get_query_scope_using_default_mode(user_input=user_request)
    
    return user_query_scope