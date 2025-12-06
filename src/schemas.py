from pydantic import BaseModel
from typing import Optional

class ExecuteRequest(BaseModel):
    language: str
    code: str
    command: Optional[str] = None

class ExecuteResponse(BaseModel):
    output: str
    exit_code: int