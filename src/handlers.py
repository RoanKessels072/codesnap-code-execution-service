import json
from src.schemas import ExecuteRequest, ExecuteResponse
from src.executor import execute_code_job

async def handle_execution_request(msg_data: dict) -> dict:
    try:
        request_model = ExecuteRequest(**msg_data)
    except Exception as e:
        return {"output": "", "error": f"Validation Error: {str(e)}", "exit_code": 400}

    result = execute_code_job(request_model.model_dump())
    
    return result