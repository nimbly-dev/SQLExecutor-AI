import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from config import settings

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

client = OpenAI()
openai.api_key = settings.OPENAI_API_KEY

class GenerateRequest(BaseModel):
    schema_: str = Field(..., alias="schema")  
    prompt: str  

    class Config:
        allow_population_by_field_name = True 

@app.get("/")
def health_check():
    return {"status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode"}

@app.post("/generate/")
async def generate(request: GenerateRequest):
    """
    Generate SQL based on the provided schema and user query using OpenAI API.
    """
    try:
        role_content = (
            "You translate user requests to SQL queries based on the provided schema. Output only the SQL."
        )

        user_content = f"""
        Schema: {request.schema_}
        User Request: {request.prompt}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"${role_content}"
                },
                {
                    "role": "user",
                    "content": f"${user_content}"
                }
            ],
            response_format={
                "type": "text"
            },
            temperature=1,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        response_dict = response.model_dump()    
        response_message = response_dict["choices"][0]["message"]["content"] 

        sql_query = response_message.strip("```").replace("sql\n", "").strip()

        usage = response_dict.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        logging.info(f"Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}, Total tokens: {total_tokens}")

        return {
            "schema": request.schema_,
            "prompt": request.prompt,
            "output": sql_query
        }

    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")
