"""Bootstrap and seed the local ERPNext demo through HTTP APIs."""

from __future__ import annotations

import json
import os
import time
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

SEED_DIR = Path(__file__).resolve().parent
MARKER_PREFIX = 'Cash-flow demo seed:'


class _ApiError(RuntimeError):
    """Represent an unsuccessful HTTP API operation."""


class _JsonApiClient:
    """Minimal JSON API client with optional cookie-backed authentication."""

    def __init__(
        self,
        base_url: str,
        *,
        cookies: bool = False,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip('/')
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            **(headers or {}),
        }
        self._opener = (
            build_opener(HTTPCookieProcessor(CookieJar()))
            if cookies
            else build_opener()
        )

    def request(
        self,
        method: str,
        path: str,
        body: Any = None,
        query: dict[str, Any] | None = None,
        *,
        timeout: float = 120,
    ) -> Any:
        """Issue a JSON request and return the decoded response body."""
        suffix = f'?{urlencode(query)}' if query else ''
        payload = None if body is None else json.dumps(body).encode('utf-8')
        request = Request(
            f'{self.base_url}{path}{suffix}',
            data=payload,
            headers=self._headers,
            method=method,
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                raw = response.read()
        except HTTPError as error:
            detail = error.read().decode('utf-8', errors='replace')
            raise _ApiError(
                f'{method} {path} returned {error.code}: {detail}'
            ) from error
        except URLError as error:
            raise _ApiError(f'{method} {path} failed: {error.reason}') from error

        result = json.loads(raw) if raw else None
        if isinstance(result, dict) and result.get('setup_wizard_failure_message'):
            raise _ApiError(
                f'{method} {path} failed: {result["setup_wizard_failure_message"]}'
            )
        return result


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _message(response: Any) -> Any:
    if not isinstance(response, dict) or 'message' not in response:
        raise _ApiError('ERPNext returned a response without a message field.')
    return response['message']


def _items(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        value = response.get('data', response.get('items', []))
        return value if isinstance(value, list) else []
    return response if isinstance(response, list) else []


def _wait_for_erpnext(client: _JsonApiClient, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            client.request('GET', '/api/method/ping', timeout=5)
            return
        except _ApiError:
            time.sleep(2)
    raise TimeoutError(
        f'ERPNext did not become ready within {timeout_seconds} seconds.'
    )


def _resource_path(doctype: str, name: str | None = None) -> str:
    path = f'/api/resource/{quote(doctype, safe="")}'
    return f'{path}/{quote(name, safe="")}' if name else path


def _find_document(
    client: _JsonApiClient,
    doctype: str,
    filters: dict[str, Any],
) -> dict[str, Any] | None:
    response = client.request(
        'GET',
        _resource_path(doctype),
        query={
            'filters': json.dumps(filters),
            'fields': json.dumps(['name', 'docstatus']),
            'limit_page_length': 1,
        },
    )
    matches = _items(response)
    if not matches:
        return None
    name = str(matches[0]['name'])
    detail = client.request('GET', _resource_path(doctype, name))
    data = detail.get('data') if isinstance(detail, dict) else None
    if not isinstance(data, dict):
        raise _ApiError(f'ERPNext returned an invalid {doctype} document.')
    return data


def _submit_document(
    client: _JsonApiClient, document: dict[str, Any]
) -> dict[str, Any]:
    response = client.request(
        'POST', '/api/method/frappe.client.submit', {'doc': document}
    )
    submitted = _message(response)
    if not isinstance(submitted, dict):
        raise _ApiError('ERPNext returned an invalid submitted document.')
    return submitted


def _ensure_document(
    client: _JsonApiClient,
    doctype: str,
    filters: dict[str, Any],
    payload: dict[str, Any],
    *,
    submit: bool = False,
) -> tuple[dict[str, Any], bool]:
    existing = _find_document(client, doctype, filters)
    created = existing is None
    if existing is None:
        response = client.request('POST', _resource_path(doctype), payload)
        existing = response.get('data') if isinstance(response, dict) else None
        if not isinstance(existing, dict):
            raise _ApiError(f'ERPNext did not return the created {doctype}.')
    if submit and int(existing.get('docstatus', 0)) == 0:
        existing = _submit_document(client, existing)
    return existing, created


def _first_named_resource(
    client: _JsonApiClient,
    doctype: str,
    filters: dict[str, Any],
) -> str:
    document = _find_document(client, doctype, filters)
    if document is None:
        raise _ApiError(f'No {doctype} matched {filters}.')
    return str(document['name'])


def _setup_erpnext(client: _JsonApiClient, setup: dict[str, Any]) -> None:
    client.request(
        'POST',
        '/api/method/login',
        {
            'usr': os.environ.get('ERPNEXT_ADMIN_USER', 'Administrator'),
            'pwd': os.environ.get('ERPNEXT_ADMIN_PASSWORD', 'admin'),
        },
    )
    client.request(
        'POST',
        '/api/method/frappe.desk.page.setup_wizard.setup_wizard.setup_complete',
        {'args': setup},
        timeout=300,
    )


def _seed_masters(client: _JsonApiClient, seed: dict[str, Any]) -> dict[str, int]:
    counts = {'created': 0, 'reused': 0}
    for customer in seed['customers']:
        _, created = _ensure_document(
            client,
            'Customer',
            {'customer_name': customer},
            {
                'customer_name': customer,
                'customer_type': 'Company',
                'customer_group': 'Commercial',
                'territory': 'India',
            },
        )
        counts['created' if created else 'reused'] += 1

    for supplier in seed['suppliers']:
        _, created = _ensure_document(
            client,
            'Supplier',
            {'supplier_name': supplier},
            {
                'supplier_name': supplier,
                'supplier_type': 'Company',
                'supplier_group': 'Services',
                'country': 'India',
            },
        )
        counts['created' if created else 'reused'] += 1

    item = seed['item']
    _, created = _ensure_document(
        client,
        'Item',
        {'item_code': item['item_code']},
        {**item, 'is_stock_item': 0},
    )
    counts['created' if created else 'reused'] += 1
    return counts


def _account_context(client: _JsonApiClient, company: str) -> dict[str, str]:
    return {
        'receivable': _first_named_resource(
            client,
            'Account',
            {'company': company, 'account_type': 'Receivable', 'is_group': 0},
        ),
        'cash': _first_named_resource(
            client,
            'Account',
            {'company': company, 'account_type': 'Cash', 'is_group': 0},
        ),
        'income': _first_named_resource(
            client,
            'Account',
            {'company': company, 'root_type': 'Income', 'is_group': 0},
        ),
        'expense': _first_named_resource(
            client,
            'Account',
            {'company': company, 'root_type': 'Expense', 'is_group': 0},
        ),
        'cost_center': _first_named_resource(
            client,
            'Cost Center',
            {'company': company, 'is_group': 0},
        ),
    }


def _marker(seed_id: str, description: str) -> str:
    return f'{MARKER_PREFIX} {seed_id} | {description}'


def _seed_transactions(
    client: _JsonApiClient,
    seed: dict[str, Any],
    accounts: dict[str, str],
) -> dict[str, int]:
    setup = seed['setup']
    company = setup['company_name']
    currency = setup['currency']
    item_code = seed['item']['item_code']
    counts = {'created': 0, 'reused': 0}

    for row in seed['sales_invoices']:
        remarks = _marker(row['seed_id'], row['description'])
        amount = float(row['amount'])
        _, created = _ensure_document(
            client,
            'Sales Invoice',
            {'remarks': remarks},
            {
                'company': company,
                'customer': row['customer'],
                'posting_date': row['posting_date'],
                'set_posting_time': 1,
                'due_date': row['due_date'],
                'currency': currency,
                'conversion_rate': 1,
                'debit_to': accounts['receivable'],
                'remarks': remarks,
                'items': [
                    {
                        'item_code': item_code,
                        'qty': 1,
                        'rate': amount,
                        'income_account': accounts['income'],
                        'cost_center': accounts['cost_center'],
                    }
                ],
            },
            submit=True,
        )
        counts['created' if created else 'reused'] += 1

    for row in seed['payment_entries']:
        amount = float(row['amount'])
        _, created = _ensure_document(
            client,
            'Payment Entry',
            {'reference_no': row['seed_id']},
            {
                'payment_type': 'Receive',
                'company': company,
                'posting_date': row['posting_date'],
                'set_posting_time': 1,
                'party_type': 'Customer',
                'party': row['party'],
                'paid_from': accounts['receivable'],
                'paid_to': accounts['cash'],
                'paid_amount': amount,
                'received_amount': amount,
                'source_exchange_rate': 1,
                'target_exchange_rate': 1,
                'reference_no': row['seed_id'],
                'reference_date': row['posting_date'],
                'remarks': _marker(row['seed_id'], row['description']),
            },
            submit=True,
        )
        counts['created' if created else 'reused'] += 1

    for row in seed['journal_entries']:
        user_remark = _marker(row['seed_id'], row['description'])
        amount = float(row['amount'])
        _, created = _ensure_document(
            client,
            'Journal Entry',
            {'user_remark': user_remark},
            {
                'voucher_type': 'Journal Entry',
                'company': company,
                'posting_date': row['posting_date'],
                'set_posting_time': 1,
                'user_remark': user_remark,
                'accounts': [
                    {
                        'account': accounts['expense'],
                        'debit_in_account_currency': amount,
                        'cost_center': accounts['cost_center'],
                    },
                    {
                        'account': accounts['cash'],
                        'credit_in_account_currency': amount,
                        'cost_center': accounts['cost_center'],
                    },
                ],
            },
            submit=True,
        )
        counts['created' if created else 'reused'] += 1
    return counts


def _ensure_integration_user(
    client: _JsonApiClient, configuration: dict[str, Any]
) -> dict[str, str]:
    email = configuration['email']
    user, _ = _ensure_document(
        client,
        'User',
        {'name': email},
        {
            'email': email,
            'first_name': configuration['first_name'],
            'enabled': 1,
            'send_welcome_email': 0,
            'user_type': 'System User',
            'roles': [{'role': configuration['role']}],
        },
    )
    roles = {str(item.get('role')) for item in user.get('roles', [])}
    if configuration['role'] not in roles:
        user['roles'] = [*user.get('roles', []), {'role': configuration['role']}]
        response = client.request('PUT', _resource_path('User', email), user)
        updated_user = response.get('data') if isinstance(response, dict) else None
        if not isinstance(updated_user, dict):
            raise _ApiError('ERPNext did not return the updated integration user.')
        user = updated_user

    response = client.request(
        'POST',
        '/api/method/frappe.core.doctype.user.user.generate_keys',
        {'user': email},
    )
    credentials = _message(response)
    if not isinstance(credentials, dict):
        raise _ApiError('ERPNext returned invalid API credentials.')
    api_key = credentials.get('api_key')
    api_secret = credentials.get('api_secret')
    if (
        not isinstance(api_key, str)
        or not api_key
        or not isinstance(api_secret, str)
        or not api_secret
    ):
        raise _ApiError('ERPNext did not return an API key and secret.')
    return {'api_key': api_key, 'api_secret': api_secret}


def _token_client(base_url: str, credentials: dict[str, str]) -> _JsonApiClient:
    return _JsonApiClient(
        base_url,
        headers={
            'Authorization': (
                f'token {credentials["api_key"]}:{credentials["api_secret"]}'
            )
        },
    )


def _verify_erpnext_credentials(
    base_url: str,
    credentials: dict[str, str],
    expected_user: str,
    *,
    attempts: int = 5,
) -> None:
    client = _token_client(base_url, credentials)
    last_error: _ApiError | None = None
    for attempt in range(attempts):
        try:
            authenticated_user = _message(
                client.request(
                    'GET',
                    '/api/method/frappe.auth.get_logged_user',
                    timeout=10,
                )
            )
            if authenticated_user != expected_user:
                raise _ApiError('ERPNext token authenticated as an unexpected user.')
            return
        except _ApiError as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(1)

    raise _ApiError(
        'ERPNext rejected the generated integration credential after '
        f'{attempts} attempts.'
    ) from last_error


def _verify_erpnext_resource_access(
    base_url: str,
    credentials: dict[str, str],
) -> None:
    client = _token_client(base_url, credentials)
    for doctype in (
        'Sales Invoice',
        'Purchase Invoice',
        'Payment Entry',
        'Journal Entry',
    ):
        try:
            response = client.request(
                'GET',
                _resource_path(doctype),
                query={
                    'fields': json.dumps(['*']),
                    'limit_page_length': 1,
                    'limit_start': 0,
                },
                timeout=15,
            )
        except _ApiError as error:
            raise _ApiError(
                f'ERPNext integration credential cannot read {doctype}: {error}'
            ) from error
        if not isinstance(response, dict) or not isinstance(response.get('data'), list):
            raise _ApiError(
                f'ERPNext returned an invalid resource response for {doctype}.'
            )


def _first_by(
    response: Any, property_name: str, expected: Any
) -> dict[str, Any] | None:
    return next(
        (item for item in _items(response) if item.get(property_name) == expected),
        None,
    )


def _configure_platform(
    client: _JsonApiClient,
    platform_seed: dict[str, Any],
    credentials: dict[str, str],
    erpnext_base_url: str,
) -> str:
    api_seed = platform_seed['api']
    enterprise_payload = api_seed['enterprise']
    enterprises = client.request(
        'GET',
        '/enterprises',
        query={'external_key': enterprise_payload['external_key']},
    )
    enterprise = _first_by(
        enterprises, 'external_key', enterprise_payload['external_key']
    )
    if enterprise is None:
        enterprise = client.request('POST', '/enterprises', enterprise_payload)

    erpnext_source_payload = next(
        source for source in api_seed['sources'] if source['source_key'] == 'erpnext'
    )
    source_path = f'/enterprises/{enterprise["id"]}/ingestion-sources'
    sources = client.request('GET', source_path, query={'source_key': 'erpnext'})
    source = _first_by(sources, 'source_key', 'erpnext')
    if source is None:
        source = client.request('POST', source_path, erpnext_source_payload)

    credential_path = f'{source_path}/{source["id"]}/credentials'
    credential_response = client.request(
        'GET', credential_path, query={'status': 'active'}
    )
    existing_credentials = _items(credential_response)
    if len(existing_credentials) > 1:
        raise _ApiError(
            'The platform returned more than one active credential for the '
            'ERPNext source.'
        )
    secret_ref = f'{credentials["api_key"]}:{credentials["api_secret"]}'
    config_json = {
        'base_url': erpnext_base_url,
        'page_size': 100,
        'timeout_seconds': 15,
        'currency_code': enterprise_payload['base_currency'],
    }
    if existing_credentials:
        credential = existing_credentials[0]
        client.request(
            'PATCH',
            f'{credential_path}/{credential["id"]}',
            {'credential_type': 'api_key', 'config_json': config_json},
        )
        credential = client.request(
            'POST',
            f'{credential_path}/{credential["id"]}/rotate',
            {'secret_ref': secret_ref},
        )
    else:
        credential = client.request(
            'POST',
            credential_path,
            {
                'credential_type': 'api_key',
                'config_json': config_json,
                'secret_ref': secret_ref,
            },
        )
    if not isinstance(credential, dict) or not credential.get('id'):
        raise _ApiError('The platform did not confirm the active ERPNext credential.')

    return f'{source_path}/{source["id"]}/sync'


def _trigger_erpnext_sync(client: _JsonApiClient, sync_path: str) -> None:
    client.request(
        'POST',
        sync_path,
        {'run_type': 'full', 'status': 'pending'},
    )


def main() -> None:
    """Seed ERPNext and connect it to the cash-flow platform.

    Raises:
        RuntimeError: If ERPNext or the platform API rejects a setup operation.
        TimeoutError: If ERPNext does not become ready within the configured limit.

    Notes:
        Generated ERPNext API credentials are passed directly to the platform and are
        never written to disk or printed. Synchronization is requested only after the
        generated token authenticates successfully before and after platform rotation.
    """
    erpnext_base_url = os.environ.get(
        'ERPNEXT_BASE_URL', 'http://erpnext-frontend:8080'
    )
    cash_flow_api_url = os.environ.get('CASH_FLOW_API_URL', 'http://api:8000')
    timeout_seconds = int(os.environ.get('ERPNEXT_READY_TIMEOUT_SECONDS', '300'))
    seed = _load_json(SEED_DIR / 'erpnext-seed-data.json')
    platform_seed = _load_json(SEED_DIR / 'seed-data.json')
    erpnext = _JsonApiClient(erpnext_base_url, cookies=True)

    print('Waiting for ERPNext...')
    _wait_for_erpnext(erpnext, timeout_seconds)
    print('Completing ERPNext setup...')
    _setup_erpnext(erpnext, seed['setup'])
    master_counts = _seed_masters(erpnext, seed)
    accounts = _account_context(erpnext, seed['setup']['company_name'])
    transaction_counts = _seed_transactions(erpnext, seed, accounts)
    credentials = _ensure_integration_user(erpnext, seed['integration_user'])
    integration_user = str(seed['integration_user']['email'])
    print('Verifying generated ERPNext credential...')
    _verify_erpnext_credentials(erpnext_base_url, credentials, integration_user)
    platform = _JsonApiClient(cash_flow_api_url)
    sync_path = _configure_platform(
        platform,
        platform_seed,
        credentials,
        erpnext_base_url,
    )
    print('Verifying ERPNext credential before synchronization...')
    _verify_erpnext_credentials(erpnext_base_url, credentials, integration_user)
    _verify_erpnext_resource_access(erpnext_base_url, credentials)
    should_sync = os.environ.get('TRIGGER_ERPNEXT_SYNC', 'true').lower() == 'true'
    if should_sync:
        _trigger_erpnext_sync(platform, sync_path)
    print(
        'ERPNext seed complete: '
        f'{master_counts["created"]} masters created, '
        f'{master_counts["reused"]} reused; '
        f'{transaction_counts["created"]} transactions created, '
        f'{transaction_counts["reused"]} reused.'
    )
    if should_sync:
        print('ERPNext credential configured and synchronization requested.')
    else:
        print('ERPNext credential configured; synchronization was disabled.')


if __name__ == '__main__':
    main()
