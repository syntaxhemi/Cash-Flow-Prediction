import { useCallback, useReducer } from 'react';

export type MutationState = { pending: boolean; error: Error | null };
type Action =
	{ type: 'pending' } | { type: 'success' } | { type: 'error'; error: Error };

type MutationAction = Action | { type: 'reset' };

function reducer(_state: MutationState, action: MutationAction): MutationState {
	if (action.type === 'pending') return { pending: true, error: null };
	if (action.type === 'success') return { pending: false, error: null };
	if (action.type === 'reset') return { pending: false, error: null };
	return { pending: false, error: action.error };
}

/** Wraps an async write operation with pending and error state. */
export function useMutation<TInput, TResult>(
	mutate: (input: TInput) => Promise<TResult>,
) {
	const [state, dispatch] = useReducer(reducer, {
		pending: false,
		error: null,
	});
	const reset = useCallback(() => {
		dispatch({ type: 'reset' });
	}, []);
	const mutateAsync = useCallback(
		async (input: TInput) => {
			dispatch({ type: 'pending' });
			try {
				const result = await mutate(input);
				dispatch({ type: 'success' });
				return result;
			} catch (reason) {
				const error =
					reason instanceof Error ? reason : new Error('Request failed');
				dispatch({ type: 'error', error });
				throw error;
			}
		},
		[mutate],
	);
	return { ...state, mutateAsync, reset };
}
