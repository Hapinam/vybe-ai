# Local development

Use Python 3.11+ (CI: 3.11 and 3.13), Node.js 22 and npm. CI and Pages use Node 22; the Docker frontend build stage uses digest-pinned Node 26. No Azure account is required. Run from the repository root in separate PowerShell terminals.

## Deterministic full-stack

API:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-test.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip check
$env:VYBE_DIRECTOR_PROVIDER = "deterministic"
.\.venv\Scripts\python.exe -m uvicorn vybe.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd apps/web
Remove-Item Env:VITE_DEMO_MODE -ErrorAction SilentlyContinue
npm.cmd ci
npm.cmd run dev
```

Open http://localhost:5173. API explorer: http://127.0.0.1:8000/docs. For entirely local execution, use a clean environment without Azure model or speech credentials. Director provider selection alone does not disable separately configured cloud narration or speech.

## Optional Ollama

Install and start Ollama locally. Pull a compatible tool-calling model, for example `ollama pull qwen3-coder:30b`. The default model may exceed available RAM/VRAM; smaller compatible models can be selected, with no guarantee of equivalent routing quality. Before starting the API set:

```powershell
$env:VYBE_DIRECTOR_PROVIDER = "ollama"
$env:VYBE_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:VYBE_OLLAMA_MODEL = "qwen3-coder:30b"
```

Only loopback HTTP endpoints with explicit ports are accepted. The adapter rejects redirects and ignores proxy settings. Ollama selects read-only tools; deterministic code answers. Provider failures fall back safely. The code default is `foundry`, not Ollama.

## Docker

From the root, with Docker running:

```powershell
docker build -t vybe:local .
docker run --rm -p 127.0.0.1:8000:8000 -e VYBE_DIRECTOR_PROVIDER=deterministic vybe:local
```

Open http://127.0.0.1:8000. The image serves React and FastAPI from one origin using `vybe.deployed:app`. Container loopback is not host loopback: host Ollama is not supported by this default container setup. Do not weaken the endpoint guard. Production Docker builds and deterministic smoke tests passed during subsequent engineering maintenance. Final fresh-clone acceptance remains pending.

## Static preview

From `apps/web`:

```powershell
npm.cmd ci
$env:VITE_DEMO_MODE = "static"
npm.cmd run build
npm.cmd run preview
```

Use the printed URL with `/vybe-ai/` base path. Clear `VITE_DEMO_MODE` before returning to full-stack mode. No live inference occurs.

See [API](../apps/api/README.md), [frontend](../apps/web/README.md), [architecture](ARCHITECTURE.md) and [testing](TESTING_AND_SECURITY.md).

## Dependency lockfile compatibility

The runtime and test lockfiles were generated on Linux
with Python 3.11. Hash-enforced installation and API tests
were validated in Linux containers using Python 3.11 and
3.13.

Native Windows installation has not been independently
validated with these lockfiles.

If installation fails on Windows, use a compatible Linux
environment or the documented Docker setup. Do not
silently bypass package hash verification.

For entirely local execution, use a clean environment
without Azure model or speech credentials. Setting the
Director provider to deterministic does not independently
disable cloud narration or speech.
