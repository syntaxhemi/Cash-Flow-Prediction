import { useCallback } from 'react';
import { api } from '@/api/client';
import { useAsyncResource } from './useAsyncResource';

/** Loads point-in-time model health snapshots for an enterprise. */
export function useStaticFinancialSnapshots(enterpriseId: string | undefined) {
	const load = useCallback(
		() =>
			enterpriseId
				? api.listStaticFinancialSnapshots(enterpriseId)
				: Promise.resolve(null),
		[enterpriseId],
	);
	return useAsyncResource(load, Boolean(enterpriseId));
}
