import logging
from fastapi import FastAPI
from pydantic import BaseModel
from model import NLPModel  
from config import settings

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 500


# Load the model
model = NLPModel()

@app.get("/")
def health_check():
    return {"status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode test"}


@app.post("/generate/")
async def generate(request: GenerateRequest):
    """
    Generate text from a given prompt using GPT-J.
    """
    try:
        output = model.generate(request.prompt, request.max_length)
        return {"prompt": request.prompt, "output": output}
    except Exception as e:
        raise Exception