from pydantic import BaseModel
from typing import Optional

class ExecuteRequest(BaseModel):
    code: str
    language: str
    mode: Optional[str] = "run"

class ExecuteResponse(BaseModel):
    output: str
    error: Optional[str] = None
    exit_code: int