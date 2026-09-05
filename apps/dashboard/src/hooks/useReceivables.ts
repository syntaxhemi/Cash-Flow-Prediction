import { useCallback } from 'react';
import { api } from '@/api/client';
import type { ReceivablesListParams } from '@/api/contracts';
import { useAsyncResource } from './useAsyncResource';

/** Loads forecast-scoped receivables and supporting invoice records. */
export function useReceivables(
	enterpriseId: string | undefined,
	params: ReceivablesListParams | null,
) {
	const load = useCallback(
		() =>
			enterpriseId && params
				? api.listReceivables(enterpriseId, params)
				: Promise.resolve(null),
		[enterpriseId, params],
	);
	return useAsyncResource(load, Boolean(enterpriseId && params));
}
