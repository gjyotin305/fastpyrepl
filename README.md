# fastpyrepl

`fastpyrepl` is a small FastAPI service that executes Python code in session-scoped environments over HTTP.

## Install

From source:

```bash
git clone https://github.com/gjyotin305/fastpyrepl
cd fastpyrepl
pip install .
```

After install, run the CLI:

```bash
fastpyrepl --help
```

## Run the server

Default:

```bash
fastpyrepl
```

Custom host/port:

```bash
fastpyrepl --host 127.0.0.1 --port 9000
```

Enable reload during development:

```bash
fastpyrepl --reload
```

The server starts at `http://<host>:<port>`.

## API Endpoints

### `GET /health`

Check service health.

Example:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status":"PYTHON REPL ACTIVE"}
```

### `POST /execute`

Execute Python code in a session.

Request body:

```json
{
  "code": "print('hello')",
  "context": "optional context string",
  "setup_code": "x = 10",
  "session_id": "optional-session-id",
  "return_locals": true,
  "locals_keys": ["x"]
}
```

Notes:
- If `session_id` is omitted, a new one is created and returned.
- Reuse the same `session_id` to keep variables between calls.
- `setup_code` runs when a new session is created.

Example:

```bash
curl -X POST http://127.0.0.1:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"x = 2\nprint(x)","return_locals":true,"locals_keys":["x"]}'
```

Response shape:

```json
{
  "stdout": "2\n",
  "stderr": "",
  "locals": {"x": 2},
  "execution_time": 0.001,
  "session_id": "...",
  "error": null
}
```

### `POST /reset`

Reset one session or all sessions.

Reset one:

```bash
curl -X POST http://127.0.0.1:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id":"your-session-id"}'
```

Reset all:

```bash
curl -X POST http://127.0.0.1:8000/reset \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Local development

```bash
python3 -m pip install -e .
fastpyrepl --reload
```

## Security warning

This service executes arbitrary Python code. Do not expose it to untrusted users or public networks without sandboxing and strict isolation.
