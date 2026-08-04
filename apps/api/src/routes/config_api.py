import os
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import dotenv_values, set_key

router = APIRouter(prefix="/config", tags=["Configuration"])

class ConfigUpdate(BaseModel):
    key: str
    value: str

@router.get("/")
def get_config():
    env_vars = dotenv_values(".env")
    return env_vars

@router.post("/")
def update_config(update: ConfigUpdate):
    if not os.path.exists(".env"):
        open(".env", "a").close()
    
    set_key(".env", update.key, str(update.value))
    
    return {"message": f"Updated {update.key} successfully."}
