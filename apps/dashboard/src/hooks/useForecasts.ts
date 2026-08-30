import { useCallback } from 'react';
import { api } from '@/api/client';
import type { ForecastListParams } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

/** Loads persisted baseline forecasts for the selected enterprise. */
export function useForecasts(
	enterpriseId: string | undefined,
	runType?: ForecastListParams['run_type'],
	status?: ForecastListParams['status'],
	limit = 50,
	offset = 0,
) {
	const load = useCallback(
		() =>
			enterpriseId
				? api.listForecasts(enterpriseId, {
						run_type: runType,
						status,
						limit,
						offset,
					})
				: Promise.resolve(null),
		[enterpriseId, limit, offset, runType, status],
	);
	return useAsyncResource(load, Boolean(enterpriseId));
}
