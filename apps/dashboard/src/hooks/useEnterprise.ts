import { useContext } from 'react';
import { EnterpriseContext } from '@/context/enterpriseContext';

/** Returns the active enterprise dashboard scope. */
export function useEnterprise() {
	const value = useContext(EnterpriseContext);
	if (!value) {
		throw new Error('useEnterprise must be used inside EnterpriseProvider');
	}
	return value;
}
