import { useCallback } from 'react';
import { api } from '@/api/client';
import type {
	ForecastRequest,
	HealthDeltaRequest,
	LiquidityMitigationRequest,
	SimulationRun,
	TrappedLiquidityRequest,
} from '@/api/contracts';
import { useMutation } from './useMutation';

type SimulationInput<T> = { forecastRunId: string; body: T };

/** Exposes forecast and simulation writes scoped to the active enterprise. */
export function useForecastMutations(enterpriseId: string | undefined) {
	const createBaseline = useMutation<
		ForecastRequest,
		Awaited<ReturnType<typeof api.createBaselineForecast>>
	>(
		useCallback(
			(body) =>
				enterpriseId
					? api.createBaselineForecast(enterpriseId, body)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const createHealthDelta = useMutation<
		SimulationInput<HealthDeltaRequest>,
		SimulationRun
	>(
		useCallback(
			({ forecastRunId, body }) =>
				enterpriseId
					? api.createHealthDeltaSimulation(enterpriseId, forecastRunId, body)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const createTrappedLiquidity = useMutation<
		SimulationInput<TrappedLiquidityRequest>,
		SimulationRun
	>(
		useCallback(
			({ forecastRunId, body }) =>
				enterpriseId
					? api.createTrappedLiquiditySimulation(
							enterpriseId,
							forecastRunId,
							body,
						)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const createLiquidityMitigation = useMutation<
		SimulationInput<LiquidityMitigationRequest>,
		SimulationRun
	>(
		useCallback(
			({ forecastRunId, body }) =>
				enterpriseId
					? api.createLiquidityMitigationSimulation(
							enterpriseId,
							forecastRunId,
							body,
						)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);

	return {
		createBaseline,
		createHealthDelta,
		createTrappedLiquidity,
		createLiquidityMitigation,
	};
}
