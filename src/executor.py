import docker
import base64
from src.config import settings

client = docker.from_env()

def run_container(image: str, code: str, ext: str, cmd_template: str):
    b64_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
    filename = f"script.{ext}"
    
    tool_cmd = cmd_template.format(filename=filename)
    shell_cmd = f'/bin/sh -c "echo {b64_code} | base64 -d > {filename} && {tool_cmd}"'

    try:
        container = client.containers.run(
            image,
            command=shell_cmd,
            mem_limit=settings.max_memory,
            network_disabled=True,
            detach=True
        )

        try:
            result = container.wait(timeout=settings.execution_timeout)
            logs = container.logs().decode('utf-8')
            exit_code = result.get('StatusCode', 1)
        except Exception:
            container.kill()
            return {"output": "", "error": "Execution timed out", "exit_code": 124}
        finally:
            try:
                container.remove(force=True)
            except:
                pass

        return {"output": logs, "error": None, "exit_code": exit_code}

    except Exception as e:
        return {"output": "", "error": str(e), "exit_code": 1}


def execute_code_job(data: dict):
    language = data.get("language")
    code = data.get("code")
    mode = data.get("mode", "run")
    
    if language == "python":
        image = settings.python_image
        ext = "py"
        if mode == "lint":
            cmd = "pylint --score=y --disable=C0114,C0116,C0304,C0103 --max-line-length=120 {filename}" 
        else:
            cmd = "python {filename}"
            
    elif language == "javascript":
        image = settings.node_image
        ext = "js"
        if mode == "lint":
            cmd = "eslint --format json --no-eslintrc --rule 'semi: off' --rule 'quotes: off' {filename}"
        else:
            cmd = "node {filename}"
            
    else:
        return {"output": "", "error": "Unsupported language", "exit_code": 1}

    return run_container(image, code, ext, cmd)