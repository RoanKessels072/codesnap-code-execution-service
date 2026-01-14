import json
from src.schemas import ExecuteRequest
from src.executor import execute_code_job

async def handle_execution_request(msg_data: dict) -> dict:
    # Used for direct "Run" requests (like the playground)
    try:
        request_model = ExecuteRequest(**msg_data)
    except Exception as e:
        return {"output": "", "error": f"Validation Error: {str(e)}", "exit_code": 400}

    result = execute_code_job(request_model.model_dump())
    return result

async def handle_grading_job(msg_data: dict) -> dict:
    """
    Orchestrates the grading process:
    1. Run the code (with test harness)
    2. Lint the original code
    Returns complete result payload.
    """
    attempt_id = msg_data.get("attempt_id")
    language = msg_data.get("language")
    
    # 1. Execute Tests
    run_payload = {
        "language": language,
        "code": msg_data.get("code"), # Harness code
        "mode": "run"
    }
    run_result = execute_code_job(run_payload)
    
    # 2. Lint Original Code
    lint_payload = {
        "language": language,
        "code": msg_data.get("original_code"),
        "mode": "lint"
    }
    lint_result = execute_code_job(lint_payload)
    
    # 3. Construct Result
    return {
        "attempt_id": attempt_id,
        "execution_output": run_result.get("output", "") + "\n" + str(run_result.get("error") or ""),
        "lint_output": lint_result.get("output", "") + "\n" + str(lint_result.get("error") or ""),
        "error": None
    }