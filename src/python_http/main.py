from threading import Lock
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from python_http.server_utils import ExecRequest, ExecResponse, SessionEnv


app = FastAPI(title="Python HTTP Executor")
_sessions: dict[str, SessionEnv] = {}
_sessions_lock = Lock()


class ResetRequest(BaseModel):
    session_id: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "PYTHON REPL ACTIVE"}


@app.post("/execute", response_model=ExecResponse)
def execute(req: ExecRequest) -> ExecResponse:
    session_id = req.session_id or str(uuid4())

    with _sessions_lock:
        env = _sessions.get(session_id)
        if env is None:
            env = SessionEnv(context=req.context, setup_code=req.setup_code)
            _sessions[session_id] = env
        elif req.context is not None:
            env.locals["context"] = req.context

    stdout, stderr, error, execution_time = env.execute(req.code)
    local_values = None
    if req.return_locals:
        if req.locals_keys:
            local_values = {key: env.locals.get(key) for key in req.locals_keys}
        else:
            local_values = dict(env.locals)

    return ExecResponse(
        stdout=stdout,
        stderr=stderr,
        locals=local_values,
        execution_time=execution_time,
        session_id=session_id,
        error=error,
    )


@app.post("/reset")
def reset(req: ResetRequest) -> dict[str, str]:
    with _sessions_lock:
        if req.session_id:
            _sessions.pop(req.session_id, None)
            return {"status": "ok", "message": f"reset session {req.session_id}"}
        _sessions.clear()
        return {"status": "ok", "message": "reset all sessions"}


if __name__ == "__main__":
    uvicorn.run("python_http.main:app", host="0.0.0.0", port=8000, reload=True)
    
