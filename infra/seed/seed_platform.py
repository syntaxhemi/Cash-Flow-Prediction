"""Run the API-owned and database demo seed stages as one operation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

SEED_DIR = Path(__file__).resolve().parent


def main() -> None:
    """Create API resources and load their related database fixture.

    Raises:
        subprocess.CalledProcessError: If either existing seed stage fails.

    Notes:
        A temporary state file transfers API-created identifiers to the database
        loader without requiring a persistent Compose volume.
    """
    api_url = os.environ.get('CASH_FLOW_API_URL', 'http://api:8000')
    with TemporaryDirectory(prefix='cash-flow-seed-') as temporary_directory:
        state_file = Path(temporary_directory) / 'seed-state.json'
        subprocess.run(
            [
                sys.executable,
                str(SEED_DIR / 'seed_api.py'),
                '--base-url',
                api_url,
                '--state-file',
                str(state_file),
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(SEED_DIR / 'seed_database.py'),
                '--state-file',
                str(state_file),
            ],
            check=True,
        )


if __name__ == '__main__':
    main()
