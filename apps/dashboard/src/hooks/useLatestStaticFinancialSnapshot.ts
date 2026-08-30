import { useCallback } from 'react';
import { api } from '@/api/client';
import { useAsyncResource } from './useAsyncResource';

/** Loads the latest model health snapshot applicable to a target date. */
export function useLatestStaticFinancialSnapshot(
	enterpriseId: string | undefined,
	targetDate: string | undefined,
) {
	const load = useCallback(
		() =>
			enterpriseId && targetDate
				? api.getLatestStaticFinancialSnapshot(enterpriseId, targetDate)
				: Promise.resolve(null),
		[enterpriseId, targetDate],
	);
	return useAsyncResource(load, Boolean(enterpriseId && targetDate));
}
