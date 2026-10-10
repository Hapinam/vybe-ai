"""Single-origin production entrypoint for the React SPA and API."""

import os
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from .main import app

static_dir = Path(os.environ.get("VYBE_STATIC_DIR", "/app/static"))

if static_dir.is_dir():
    # Mount last: API routes (/health and /v1/...) retain precedence.
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="web")
