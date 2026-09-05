import { useCallback } from 'react';
import { api } from '@/api/client';
import type { IngestionRunListParams } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

/**
 * Loads synchronization runs for one or more enterprise ingestion sources.
 *
 * Args:
 *     enterpriseId: Enterprise identifier used to scope the request.
 *     sourceId: One source identifier or a collection of source identifiers.
 *     status: Optional run-status filter.
 *     runType: Optional run-type filter.
 *     limit: Number of runs returned after aggregation.
 *     offset: Number of aggregated runs to skip.
 *
 * Returns:
 *     An asynchronous resource containing the requested ingestion runs.
 *
 * Notes:
 *     Multiple sources are fetched through the existing source-scoped API and
 *     merged in descending creation-time order for enterprise-wide history.
 */
export function useIngestionRuns(
	enterpriseId: string | undefined,
	sourceId: string | readonly string[] | undefined,
	status?: IngestionRunListParams['status'],
	runType?: IngestionRunListParams['run_type'],
	limit = 100,
	offset = 0,
) {
	const sourceIds =
		typeof sourceId === 'string' ? [sourceId] : (sourceId ?? []);
	const sourceIdsKey = sourceIds.join(',');
	const load = useCallback(
		async () => {
			const requestedSourceIds = sourceIdsKey ? sourceIdsKey.split(',') : [];
			if (!enterpriseId || requestedSourceIds.length === 0) return null;
			if (requestedSourceIds.length === 1) {
				return api.listIngestionRuns(enterpriseId, requestedSourceIds[0], {
					status,
					run_type: runType,
					limit,
					offset,
				});
			}

			const responses = await Promise.all(
				requestedSourceIds.map((id) =>
					api.listIngestionRuns(enterpriseId, id, {
						status,
						run_type: runType,
						limit: 200,
						offset: 0,
					}),
				),
			);
			const items = responses
				.flatMap((response) => response.items)
				.sort(
					(left, right) =>
						new Date(right.created_at).getTime() -
						new Date(left.created_at).getTime(),
				);
			const pageItems = items.slice(offset, offset + limit);

			return {
				items: pageItems,
				pagination: {
					limit,
					offset,
					total_count: items.length,
					has_next: offset + pageItems.length < items.length,
					has_prev: offset > 0,
				},
			};
		},
		[enterpriseId, limit, offset, runType, sourceIdsKey, status],
	);
	return useAsyncResource(load, Boolean(enterpriseId && sourceIds.length > 0));
}
