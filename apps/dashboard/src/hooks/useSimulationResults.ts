import { useCallback } from 'react';
import { api } from '@/api/client';
import type { SimulationListParams } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

/** Loads persisted simulation results for the selected enterprise. */
export function useSimulationResults(
	enterpriseId: string | undefined,
	simulationType?: SimulationListParams['simulation_type'],
	status?: SimulationListParams['status'],
	createdFrom?: SimulationListParams['created_from'],
	createdTo?: SimulationListParams['created_to'],
	limit = 100,
	offset = 0,
) {
	const load = useCallback(
		() =>
			enterpriseId
				? api.listSimulationResults(enterpriseId, {
						simulation_type: simulationType,
						status,
						created_from: createdFrom,
						created_to: createdTo,
						limit,
						offset,
					})
				: Promise.resolve(null),
		[
			createdFrom,
			createdTo,
			enterpriseId,
			limit,
			offset,
			simulationType,
			status,
		],
	);
	return useAsyncResource(load, Boolean(enterpriseId));
}
