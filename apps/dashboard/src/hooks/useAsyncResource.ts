import { useCallback, useEffect, useReducer, useRef } from 'react';

export type AsyncResourceState<T> = {
	data: T | null;
	loading: boolean;
	error: Error | null;
};

type Action<T> =
	| { type: 'loading' }
	| { type: 'success'; data: T }
	| { type: 'error'; error: Error }
	| { type: 'reset' };

function reducer<T>(
	state: AsyncResourceState<T>,
	action: Action<T>,
): AsyncResourceState<T> {
	if (action.type === 'loading')
		return { ...state, loading: true, error: null };
	if (action.type === 'success')
		return { data: action.data, loading: false, error: null };
	if (action.type === 'reset') return { data: null, loading: false, error: null };
	return { ...state, loading: false, error: action.error };
}

/** Runs an async resource loader and ignores stale responses after refreshes. */
export function useAsyncResource<T>(load: () => Promise<T>, enabled = true) {
	const [state, dispatch] = useReducer(reducer<T>, {
		data: null,
		loading: enabled,
		error: null,
	});
	const requestVersion = useRef(0);

	const refresh = useCallback(async () => {
		if (!enabled) return;

		const version = ++requestVersion.current;
		dispatch({ type: 'loading' });
		try {
			const data = await load();
			if (version === requestVersion.current) {
				dispatch({ type: 'success', data });
			}
		} catch (reason) {
			if (version === requestVersion.current) {
				dispatch({
					type: 'error',
					error: reason instanceof Error ? reason : new Error('Request failed'),
				});
			}
		}
	}, [enabled, load]);

	useEffect(() => {
		if (!enabled) {
			dispatch({ type: 'reset' });
			return;
		}
		void refresh();
		return () => {
			requestVersion.current += 1;
		};
	}, [enabled, refresh]);

	return { ...state, refresh };
}
