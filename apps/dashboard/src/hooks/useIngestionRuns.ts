import { useCallback } from 'react';
import { api } from '@/api/client';
import type { IngestionRunListParams } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

/** Loads synchronization runs for one enterprise ingestion source. */
export function useIngestionRuns(
	enterpriseId: string | undefined,
	sourceId: string | undefined,
	status?: IngestionRunListParams['status'],
	runType?: IngestionRunListParams['run_type'],
	limit = 100,
	offset = 0,
) {
	const load = useCallback(
		() =>
			enterpriseId && sourceId
				? api.listIngestionRuns(enterpriseId, sourceId, {
						status,
						run_type: runType,
						limit,
						offset,
					})
				: Promise.resolve(null),
		[enterpriseId, limit, offset, runType, sourceId, status],
	);
	return useAsyncResource(load, Boolean(enterpriseId && sourceId));
}
