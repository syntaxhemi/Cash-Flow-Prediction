import { createContext } from 'react';
import type { Enterprise } from '@/api/contracts';

export type EnterpriseContextValue = {
	enterprise: Enterprise | null;
	enterpriseId: string | null;
	enterprises: Enterprise[];
	loading: boolean;
	error: string | null;
	refresh: () => Promise<void>;
	setEnterpriseId: (id: string) => void;
};

export const EnterpriseContext = createContext<EnterpriseContextValue | null>(
	null,
);
