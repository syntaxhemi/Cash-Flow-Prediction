import { useCallback } from 'react';
import { api } from '@/api/client';
import { useAsyncResource } from './useAsyncResource';

/** Loads ingestion sources for the selected enterprise. */
export function useIngestionSources(enterpriseId: string | undefined) {
	const load = useCallback(
		() =>
			enterpriseId
				? api.listIngestionSources(enterpriseId, {
						is_active: true,
						limit: 100,
						offset: 0,
					})
				: Promise.resolve(null),
		[enterpriseId],
	);
	return useAsyncResource(load, Boolean(enterpriseId));
}
