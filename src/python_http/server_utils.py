from pydantic import BaseModel
from typing import Any, List, Dict, Optional
import time

class ExecRequest(BaseModel):
    code: str
    context: Optional[str] = None
    setup_code: Optional[str] = None
    session_id: Optional[str] = None
    return_locals: bool = False
    locals_keys: Optional[List[str]] = None

class ExecResponse(BaseModel):
    stdout: str
    stderr: str
    locals: Optional[Dict[str, Any]] = None
    execution_time: float
    session_id: str
    error: Optional[str] = None

class SessionEnv:
    def __init__(self, context=None, setup_code=None) -> None:
        self.globals = {'__builtins__': __builtins__}
        self.locals = {}
        if context is not None:
            self.locals["context"] = context
        if setup_code:
            self.execute(setup_code)
    
    def execute(self, code: str):
        import io, sys
        start = time.time()
        stdout = io.StringIO()
        stderr = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = stdout, stderr
            exec(code, self.globals, self.locals)
            return stdout.getvalue(), stderr.getvalue(), None, time.time() - start
        except Exception as e:
            return stdout.getvalue(), stderr.getvalue() + str(e), str(e), time.time() - start
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr


# if __name__ == "__main__":
#     test_code = """import numpy as np
# a = np.array([1, 2, 3, 4, 5], dtype=float)
# b = np.array([5, 4, 3, 2, 1], dtype=float)
# print("a + b:", a + b)
# print("a * b:", a * b)
# print("mean(a):", np.mean(a))
# m = np.array([[1, 2], [3, 4]], dtype=float)
# print("matrix:\\n", m)
# print("transpose:\\n", m.T)
# print("determinant:", np.linalg.det(m))"""
#     env = SessionEnv(
#         context="",
#     )
#     stdout, stderr, error, execution_time = env.execute(test_code)
#     print(stderr)
#     print(env.locals)
