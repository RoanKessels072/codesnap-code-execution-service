from src.schemas import ExecuteCodeRequest, ExecutionResult
from src.executor import execute_code

async def handle_execute_code(data: dict):
    try:
        req = ExecuteCodeRequest(**data)
    except Exception as e:
        return {"error": f"Invalid request format: {str(e)}"}

    result_dict = execute_code(req.code, req.language)
    
    return ExecutionResult(**result_dict).model_dump(mode='json')