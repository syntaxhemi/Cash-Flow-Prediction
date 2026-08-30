import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { api } from '@/api/client';
import { EnterpriseContext } from '@/context/enterpriseContext';

const ENTERPRISE_STORAGE_KEY = 'cash-flow-enterprise-id';

/** Provides the active enterprise and its available dashboard scope. */
export function EnterpriseProvider({ children }: { children: ReactNode }) {
	const [enterprises, setEnterprises] = useState<
		Awaited<ReturnType<typeof api.listEnterprises>>['items']
	>([]);
	const [enterpriseId, setEnterpriseIdState] = useState<string | null>(() =>
		localStorage.getItem(ENTERPRISE_STORAGE_KEY),
	);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const refresh = useCallback(async () => {
		setLoading(true);
		setError(null);
		try {
			const response = await api.listEnterprises({
				is_active: true,
				limit: 100,
				offset: 0,
			});
			setEnterprises(response.items);
			setEnterpriseIdState((currentId) => {
				const selectedId =
					currentId && response.items.some((item) => item.id === currentId)
						? currentId
						: (response.items[0]?.id ?? null);
				if (selectedId)
					localStorage.setItem(ENTERPRISE_STORAGE_KEY, selectedId);
				else localStorage.removeItem(ENTERPRISE_STORAGE_KEY);
				return selectedId;
			});
		} catch (reason) {
			setError(
				reason instanceof Error ? reason.message : 'Unable to load enterprises',
			);
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		queueMicrotask(() => void refresh());
	}, [refresh]);

	const changeEnterprise = useCallback((id: string) => {
		setEnterpriseIdState(id);
		localStorage.setItem(ENTERPRISE_STORAGE_KEY, id);
	}, []);

	const value = useMemo(
		() => ({
			enterprise: enterprises.find((item) => item.id === enterpriseId) ?? null,
			enterpriseId,
			enterprises,
			loading,
			error,
			refresh,
			setEnterpriseId: changeEnterprise,
		}),
		[changeEnterprise, enterpriseId, enterprises, error, loading, refresh],
	);

	return (
		<EnterpriseContext.Provider value={value}>
			{children}
		</EnterpriseContext.Provider>
	);
}
