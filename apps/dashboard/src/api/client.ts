import type {
	Enterprise,
	EnterpriseCreate,
	EnterpriseListParams,
	EnterpriseListResponse,
	EnterpriseUpdate,
	ForecastRequest,
	ForecastListParams,
	ForecastListResponse,
	ForecastRun,
	HealthDeltaRequest,
	IngestionRun,
	IngestionRunCreate,
	IngestionRunListParams,
	IngestionRunListResponse,
	IngestionSource,
	IngestionSourceCreate,
	IngestionSourceListParams,
	IngestionSourceListResponse,
	IngestionSourceUpdate,
	LiquidityMitigationRequest,
	ReceivablesListParams,
	ReceivablesListResponse,
	SimulationListParams,
	SimulationRun,
	StaticFinancialSnapshot,
	StaticFinancialSnapshotCreate,
	StaticFinancialSnapshotUpdate,
	TrappedLiquidityRequest,
} from './contracts';

/** Error raised when an API request does not return a successful response. */
export type ApiError = Error & { status?: number; detail?: unknown };

const baseUrl = (
	import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
).replace(/\/$/, '');

function errorMessage(detail: unknown, status: number): string {
	if (typeof detail === 'string' && detail) return detail;
	if (Array.isArray(detail)) {
		const messages = detail
			.map((item) =>
				item && typeof item === 'object' && 'msg' in item
					? String(item.msg)
					: null,
			)
			.filter(Boolean);
		if (messages.length) return messages.join(', ');
	}
	if (detail && typeof detail === 'object' && 'detail' in detail) {
		return errorMessage(detail.detail, status);
	}
	if (detail && typeof detail === 'object' && 'error' in detail) {
		return errorMessage(detail.error, status);
	}
	if (detail && typeof detail === 'object' && 'message' in detail) {
		return String(detail.message);
	}
	return `Request failed (${status})`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
	const headers = new Headers(init.headers);
	const isFormData = init.body instanceof FormData;
	if (!isFormData && !headers.has('Content-Type')) {
		headers.set('Content-Type', 'application/json');
	}

	const response = await fetch(`${baseUrl}${path}`, { ...init, headers });
	const body = response.status === 204 ? null : await response.text();

	if (!response.ok) {
		let detail: unknown;
		if (body) {
			try {
				detail = JSON.parse(body);
			} catch {
				// Keep the HTTP status as the fallback error message.
			}
		}
		const error = new Error(errorMessage(detail, response.status)) as ApiError;
		error.status = response.status;
		error.detail = detail;
		throw error;
	}

	return (body ? JSON.parse(body) : undefined) as T;
}

function query(
	params: Record<string, string | number | boolean | null | undefined>,
): string {
	const values = Object.entries(params).filter(
		([, value]) => value !== undefined && value !== null && value !== '',
	);
	return values.length
		? `?${new URLSearchParams(
				values.map(([key, value]) => [key, String(value)]),
			)}`
		: '';
}

/** Typed HTTP accessors for the dashboard-facing FastAPI endpoints. */
export const api = {
	listEnterprises: (params: EnterpriseListParams = {}) =>
		request<EnterpriseListResponse>(`/enterprises${query(params)}`),
	getEnterprise: (enterpriseId: string) =>
		request<Enterprise>(`/enterprises/${enterpriseId}`),
	createEnterprise: (body: EnterpriseCreate) =>
		request<Enterprise>('/enterprises', {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	updateEnterprise: (enterpriseId: string, body: EnterpriseUpdate) =>
		request<Enterprise>(`/enterprises/${enterpriseId}`, {
			method: 'PATCH',
			body: JSON.stringify(body),
		}),

	listIngestionSources: (
		enterpriseId: string,
		params: IngestionSourceListParams = {},
	) =>
		request<IngestionSourceListResponse>(
			`/enterprises/${enterpriseId}/ingestion-sources${query(params)}`,
		),
	getIngestionSource: (enterpriseId: string, sourceId: string) =>
		request<IngestionSource>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}`,
		),
	createIngestionSource: (enterpriseId: string, body: IngestionSourceCreate) =>
		request<IngestionSource>(`/enterprises/${enterpriseId}/ingestion-sources`, {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	updateIngestionSource: (
		enterpriseId: string,
		sourceId: string,
		body: IngestionSourceUpdate,
	) =>
		request<IngestionSource>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}`,
			{ method: 'PATCH', body: JSON.stringify(body) },
		),
	deleteIngestionSource: (enterpriseId: string, sourceId: string) =>
		request<void>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}`,
			{ method: 'DELETE' },
		),
	requestIngestionSync: (
		enterpriseId: string,
		sourceId: string,
		body: IngestionRunCreate,
	) =>
		request<IngestionRun>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}/sync`,
			{ method: 'POST', body: JSON.stringify(body) },
		),
	uploadIngestionFile: (
		enterpriseId: string,
		sourceId: string,
		file: File,
		sheetName?: string,
	) => {
		const body = new FormData();
		body.append('file', file);
		if (sheetName) body.append('sheet_name', sheetName);
		return request<IngestionRun>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}/upload`,
			{ method: 'POST', body },
		);
	},
	listIngestionRuns: (
		enterpriseId: string,
		sourceId: string,
		params: IngestionRunListParams = {},
	) =>
		request<IngestionRunListResponse>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}/runs${query(params)}`,
		),
	getIngestionRun: (enterpriseId: string, sourceId: string, runId: string) =>
		request<IngestionRun>(
			`/enterprises/${enterpriseId}/ingestion-sources/${sourceId}/runs/${runId}`,
		),

	listStaticFinancialSnapshots: (enterpriseId: string) =>
		request<StaticFinancialSnapshot[]>(
			`/enterprises/${enterpriseId}/financial/static-snapshots`,
		),
	getLatestStaticFinancialSnapshot: (
		enterpriseId: string,
		targetDate: string,
	) =>
		request<StaticFinancialSnapshot>(
			`/enterprises/${enterpriseId}/financial/static-snapshots/latest${query({ target_date: targetDate })}`,
		),
	createStaticFinancialSnapshot: (
		enterpriseId: string,
		body: StaticFinancialSnapshotCreate,
	) =>
		request<StaticFinancialSnapshot>(
			`/enterprises/${enterpriseId}/financial/static-snapshots`,
			{ method: 'POST', body: JSON.stringify(body) },
		),
	updateStaticFinancialSnapshot: (
		enterpriseId: string,
		snapshotId: string,
		body: StaticFinancialSnapshotUpdate,
	) =>
		request<StaticFinancialSnapshot>(
			`/enterprises/${enterpriseId}/financial/static-snapshots/${snapshotId}`,
			{ method: 'PATCH', body: JSON.stringify(body) },
		),

	createBaselineForecast: (enterpriseId: string, body: ForecastRequest) =>
		request<ForecastRun>(`/enterprises/${enterpriseId}/forecasts`, {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	listForecasts: (enterpriseId: string, params: ForecastListParams = {}) =>
		request<ForecastListResponse>(
			`/enterprises/${enterpriseId}/forecasts${query(params)}`,
		),
	listReceivables: (
		enterpriseId: string,
		params: ReceivablesListParams,
	) =>
		request<ReceivablesListResponse>(
			`/enterprises/${enterpriseId}/receivables${query(params)}`,
		),
	getForecast: (enterpriseId: string, forecastRunId: string) =>
		request<ForecastRun>(
			`/enterprises/${enterpriseId}/forecasts/${forecastRunId}`,
		),
	createHealthDeltaSimulation: (
		enterpriseId: string,
		forecastRunId: string,
		body: HealthDeltaRequest,
	) =>
		request<SimulationRun>(
			`/enterprises/${enterpriseId}/forecasts/${forecastRunId}/simulations/health-delta`,
			{ method: 'POST', body: JSON.stringify(body) },
		),
	createTrappedLiquiditySimulation: (
		enterpriseId: string,
		forecastRunId: string,
		body: TrappedLiquidityRequest,
	) =>
		request<SimulationRun>(
			`/enterprises/${enterpriseId}/forecasts/${forecastRunId}/simulations/trapped-liquidity`,
			{ method: 'POST', body: JSON.stringify(body) },
		),
	createLiquidityMitigationSimulation: (
		enterpriseId: string,
		forecastRunId: string,
		body: LiquidityMitigationRequest,
	) =>
		request<SimulationRun>(
			`/enterprises/${enterpriseId}/forecasts/${forecastRunId}/simulations/liquidity-mitigation`,
			{ method: 'POST', body: JSON.stringify(body) },
		),
	listSimulationResults: (
		enterpriseId: string,
		params: SimulationListParams = {},
	) =>
		request<SimulationRun[]>(
			`/enterprises/${enterpriseId}/simulations${query(params)}`,
		),
	getSimulationResult: (enterpriseId: string, simulationRunId: string) =>
		request<SimulationRun>(
			`/enterprises/${enterpriseId}/simulations/${simulationRunId}`,
		),
};
