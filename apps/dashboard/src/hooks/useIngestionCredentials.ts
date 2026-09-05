import { useCallback } from 'react';
import { api } from '@/api/client';
import type { IngestionSourceCredentialListParams } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

/** Loads credential metadata for one ingestion source. */
export function useIngestionCredentials(
	enterpriseId: string | undefined,
	sourceId: string | undefined,
	status?: IngestionSourceCredentialListParams['status'],
) {
	const load = useCallback(
		() =>
			enterpriseId && sourceId
				? api.listIngestionSourceCredentials(enterpriseId, sourceId, {
						status,
						limit: 20,
						offset: 0,
					})
				: Promise.resolve(null),
		[enterpriseId, sourceId, status],
	);
	return useAsyncResource(load, Boolean(enterpriseId && sourceId));
}
