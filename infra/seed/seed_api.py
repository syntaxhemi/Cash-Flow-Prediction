"""Create or reuse API-owned resources required by the demo seed."""

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SEED_DIR = Path(__file__).resolve().parent


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _api_call(
    base_url: str,
    method: str,
    path: str,
    body: Any = None,
) -> Any:
    payload = None if body is None else json.dumps(body).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    request = Request(
        f'{base_url.rstrip("/")}{path}',
        data=payload,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request) as response:
            raw = response.read()
    except (HTTPError, URLError) as error:
        detail = (
            error.read().decode('utf-8', errors='replace')
            if isinstance(error, HTTPError)
            else str(error)
        )
        raise RuntimeError(f'{method} {path} failed: {detail}') from error
    return json.loads(raw) if raw else None


def _items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return value.get('items', [])
    return value or []


def _first_by(items: Any, property_name: str, value: Any) -> dict[str, Any] | None:
    return next(
        (item for item in _items(items) if item.get(property_name) == value),
        None,
    )


def _ensure_enterprise(base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    enterprises = _api_call(
        base_url,
        'GET',
        f'/enterprises?external_key={payload["external_key"]}',
    )
    enterprise = _first_by(enterprises, 'external_key', payload['external_key'])
    return enterprise or _api_call(base_url, 'POST', '/enterprises', payload)


def _ensure_source(
    base_url: str,
    enterprise_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    sources = _api_call(
        base_url,
        'GET',
        f'/enterprises/{enterprise_id}/ingestion-sources?source_key={payload["source_key"]}',
    )
    source = _first_by(sources, 'source_key', payload['source_key'])
    return source or _api_call(
        base_url,
        'POST',
        f'/enterprises/{enterprise_id}/ingestion-sources',
        payload,
    )


def _ensure_credential(
    base_url: str,
    enterprise_id: str,
    source_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    credentials = _api_call(
        base_url,
        'GET',
        f'/enterprises/{enterprise_id}/ingestion-sources/{source_id}/credentials',
    )
    existing = _items(credentials)
    if existing:
        return existing[0]
    return _api_call(
        base_url,
        'POST',
        f'/enterprises/{enterprise_id}/ingestion-sources/{source_id}/credentials',
        payload,
    )


def main() -> None:
    """Create or reuse the demo enterprise, sources, and ERPNext credential."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://localhost:8000')
    parser.add_argument('--seed-file', type=Path, default=SEED_DIR / 'seed-data.json')
    parser.add_argument('--state-file', type=Path, default=SEED_DIR / 'seed-state.json')
    args = parser.parse_args()

    seed = _load_json(args.seed_file)
    api_seed = seed['api']
    enterprise = _ensure_enterprise(args.base_url, api_seed['enterprise'])
    sources = {
        item['source_key']: _ensure_source(args.base_url, enterprise['id'], item)
        for item in api_seed['sources']
    }
    credential = _ensure_credential(
        args.base_url,
        enterprise['id'],
        sources['erpnext']['id'],
        api_seed['erpnext_credential'],
    )

    state = {
        'enterprise_id': enterprise['id'],
        'erpnext_source_id': sources['erpnext']['id'],
        'csv_source_id': sources['csv']['id'],
        'erpnext_credential_id': credential['id'],
    }
    args.state_file.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    print(f'API seed resources ready for enterprise {enterprise["id"]}.')
    print(f'State written to {args.state_file}; do not commit generated state.')


if __name__ == '__main__':
    main()
