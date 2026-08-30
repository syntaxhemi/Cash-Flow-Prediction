import type { components, operations } from './generated/types';

/** Application aliases for the generated OpenAPI contracts. */
export type Enterprise = components['schemas']['EnterpriseSchema'];
export type EnterpriseCreate = components['schemas']['EnterpriseCreateSchema'];
export type EnterpriseUpdate = components['schemas']['EnterpriseUpdateSchema'];
export type EnterpriseListResponse =
	components['schemas']['EnterpriseListResponse'];

export type IngestionSource = components['schemas']['IngestionSourceSchema'];
export type IngestionSourceCreate =
	components['schemas']['IngestionSourceCreateSchema'];
export type IngestionSourceUpdate =
	components['schemas']['IngestionSourceUpdateSchema'];
export type IngestionSourceListResponse =
	components['schemas']['IngestionSourceListResponse'];

export type IngestionRun = components['schemas']['IngestionRunSchema'];
export type IngestionRunCreate =
	components['schemas']['IngestionRunCreateSchema'];
export type IngestionRunListResponse =
	components['schemas']['IngestionRunListResponse'];

export type IngestionSourceCredential =
	components['schemas']['IngestionSourceCredentialSchema'];
export type IngestionSourceCredentialCreate =
	components['schemas']['IngestionSourceCredentialCreateSchema'];
export type IngestionSourceCredentialMetadataUpdate =
	components['schemas']['IngestionSourceCredentialMetadataUpdateSchema'];
export type IngestionSourceCredentialSecretUpdate =
	components['schemas']['IngestionSourceCredentialSecretUpdateSchema'];
export type IngestionSourceCredentialListResponse =
	components['schemas']['IngestionSourceCredentialListResponse'];

export type StaticFinancialSnapshot =
	components['schemas']['StaticFinancialSnapshotSchema'];
export type StaticFinancialSnapshotCreate =
	components['schemas']['StaticFinancialSnapshotCreateSchema'];
export type StaticFinancialSnapshotUpdate =
	components['schemas']['StaticFinancialSnapshotUpdateSchema'];

export type ForecastRequest = components['schemas']['ForecastRequestSchema'];
export type ForecastRun = components['schemas']['ForecastRunSchema'];

export type HealthDeltaRequest =
	components['schemas']['HealthDeltaRequestSchema'];
export type TrappedLiquidityRequest =
	components['schemas']['TrappedLiquidityRequestSchema'];
export type LiquidityMitigationRequest =
	components['schemas']['LiquidityMitigationRequestSchema'];
export type SimulationRun = components['schemas']['SimulationRunSchema'];

export type EnterpriseListParams = NonNullable<
	operations['list_enterprises_enterprises_get']['parameters']['query']
>;
export type IngestionSourceListParams = NonNullable<
	operations['list_ingestion_sources_enterprises__enterprise_id__ingestion_sources_get']['parameters']['query']
>;
export type IngestionRunListParams = NonNullable<
	operations['list_ingestion_runs_enterprises__enterprise_id__ingestion_sources__source_id__runs_get']['parameters']['query']
>;
export type IngestionSourceCredentialListParams = NonNullable<
	operations['list_ingestion_source_credentials_enterprises__enterprise_id__ingestion_sources__source_id__credentials_get']['parameters']['query']
>;
export type SimulationListParams = NonNullable<
	operations['list_simulation_results_enterprises__enterprise_id__simulations_get']['parameters']['query']
>;
