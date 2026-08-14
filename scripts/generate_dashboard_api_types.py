"""Generate TypeScript API types from the FastAPI OpenAPI document."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / 'apps' / 'dashboard'
OUTPUT_PATH = DASHBOARD_DIR / 'src' / 'api' / 'generated' / 'types.ts'
API_SOURCE_DIR = REPO_ROOT / 'apps' / 'api' / 'src'

if str(API_SOURCE_DIR) not in sys.path:
	sys.path.insert(0, str(API_SOURCE_DIR))

from api.main import create_application


def _resolve_npm_command() -> str:
    """Return the npm executable available on the current platform.

    Returns:
            The resolved npm executable name.

    Raises:
            RuntimeError: If npm cannot be found on ``PATH``.
    """
    for candidate in ('npm.cmd', 'npm'):
        executable = shutil.which(candidate)
        if executable is not None:
            return executable
    raise RuntimeError('Unable to locate npm in PATH.')


def main() -> int:
    """Generate dashboard TypeScript types from the application OpenAPI schema.

    Returns:
            The exit code returned by ``openapi-typescript``.
    """
    app = create_application()
    openapi_schema = app.openapi()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        schema_path = Path(temp_dir) / 'openapi.json'
        schema_path.write_text(
            json.dumps(openapi_schema, indent=2),
            encoding='utf-8',
        )

        command = [
            _resolve_npm_command(),
            'exec',
            '--prefix',
            str(DASHBOARD_DIR),
            'openapi-typescript',
            '--',
            str(schema_path),
            '-o',
            str(OUTPUT_PATH),
        ]
        result = subprocess.run(command, check=False, cwd=REPO_ROOT)
        return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
