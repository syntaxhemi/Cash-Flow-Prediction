import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import InlineError from '@/components/ui/InlineError';
import ResourceError from '@/components/ui/ResourceError';
import { useEnterprise } from '@/hooks/useEnterprise';
import { useForecastMutations } from '@/hooks/useForecastMutations';
import { useForecasts } from '@/hooks/useForecasts';
import { useReceivables } from '@/hooks/useReceivables';
import { useSimulationResults } from '@/hooks/useSimulationResults';
import { toReceivablesView } from '../receivables/adapters';
import CashPosition from './CashPosition';
import DraftScenarioCard from './DraftScenarioCard';
import {
	DesktopMitigationSpectrum,
	MobileMitigationSpectrum,
} from './MitigationSpectrum';
import PlanningSkeleton from './PlanningSkeleton';
import RecommendationCard from './RecommendationCard';
import { toPlanningView } from './adapters';

function PlanningPage() {
	const { enterpriseId } = useEnterprise();
	const forecasts = useForecasts(
		enterpriseId ?? undefined,
		'ad_hoc_baseline',
		'completed',
		1,
		0,
	);
	const latestForecast = forecasts.data?.items[0] ?? null;
	const receivableParams = useMemo(
		() =>
			latestForecast
				? {
						forecast_run_id: latestForecast.id,
						account_filter: 'all' as const,
						horizon_days: '30' as const,
					}
				: null,
		[latestForecast],
	);
	const receivables = useReceivables(
		enterpriseId ?? undefined,
		receivableParams,
	);
	const mitigationSimulations = useSimulationResults(
		enterpriseId ?? undefined,
		'liquidity_mitigation',
		'completed',
		undefined,
		undefined,
		100,
		0,
	);
	const trappedLiquiditySimulations = useSimulationResults(
		enterpriseId ?? undefined,
		'trapped_liquidity',
		'completed',
		undefined,
		undefined,
		100,
		0,
	);
	const { refresh: refreshMitigationSimulations } = mitigationSimulations;
	const { refresh: refreshTrappedLiquiditySimulations } =
		trappedLiquiditySimulations;
	const { createLiquidityMitigation, createTrappedLiquidity } =
		useForecastMutations(enterpriseId ?? undefined);
	const [activeMitigation, setActiveMitigation] = useState<
		Awaited<ReturnType<typeof createLiquidityMitigation.mutateAsync>> | null
	>(null);
	const [activeTrappedLiquidity, setActiveTrappedLiquidity] = useState<
		Awaited<ReturnType<typeof createTrappedLiquidity.mutateAsync>> | null
	>(null);
	const initialMitigationForecast = useRef<string | null>(null);
	const initialTrappedForecast = useRef<string | null>(null);

	const latestMitigation = mitigationSimulations.data?.find(
		(simulation) => simulation.forecast_run_id === latestForecast?.id,
	);
	const latestTrappedLiquidity = trappedLiquiditySimulations.data?.find(
		(simulation) => simulation.forecast_run_id === latestForecast?.id,
	);
	const mitigationResult =
		activeMitigation?.forecast_run_id === latestForecast?.id
			? activeMitigation
			: latestMitigation ?? null;
	const trappedLiquidityResult =
		activeTrappedLiquidity?.forecast_run_id === latestForecast?.id
			? activeTrappedLiquidity
			: latestTrappedLiquidity ?? null;
	const hasActiveMitigation = Boolean(
		activeMitigation?.forecast_run_id === latestForecast?.id,
	);
	const hasActiveTrappedLiquidity = Boolean(
		activeTrappedLiquidity?.forecast_run_id === latestForecast?.id,
	);

	const receivableView =
		receivables.data && trappedLiquidityResult
			? toReceivablesView(receivables.data, trappedLiquidityResult).items
			: [];
	const view = latestForecast
		? toPlanningView(latestForecast, mitigationResult, receivableView)
		: null;

	const runMitigation = useCallback(async () => {
		if (!latestForecast) {
			throw new Error(
				'A completed forecast is required before generating a cash plan.',
			);
		}
		const result = await createLiquidityMitigation.mutateAsync({
			forecastRunId: latestForecast.id,
			body: { profile: 'standard', max_recommendations: 3 },
		});
		setActiveMitigation(result);
		void refreshMitigationSimulations();
		return result;
	}, [
		createLiquidityMitigation,
		latestForecast,
		refreshMitigationSimulations,
	]);

	const runTrappedLiquidity = useCallback(async () => {
		if (!latestForecast) {
			throw new Error(
				'A completed forecast is required before identifying collection opportunities.',
			);
		}
		const result = await createTrappedLiquidity.mutateAsync({
			forecastRunId: latestForecast.id,
			body: { counterparty_ids: null, max_counterparties: 50 },
		});
		setActiveTrappedLiquidity(result);
		void refreshTrappedLiquiditySimulations();
		return result;
	}, [createTrappedLiquidity, latestForecast, refreshTrappedLiquiditySimulations]);

	useEffect(() => {
		if (
			!latestForecast ||
			forecasts.loading ||
			forecasts.error ||
			receivables.loading ||
			receivables.error ||
			trappedLiquiditySimulations.loading ||
			trappedLiquiditySimulations.error ||
			latestTrappedLiquidity ||
			hasActiveTrappedLiquidity ||
			createTrappedLiquidity.pending ||
			createTrappedLiquidity.error ||
			initialTrappedForecast.current === latestForecast.id
		) {
			return;
		}
		initialTrappedForecast.current = latestForecast.id;
		void runTrappedLiquidity().catch(() => undefined);
	}, [
		activeTrappedLiquidity,
		createTrappedLiquidity.error,
		createTrappedLiquidity.pending,
		forecasts.error,
		forecasts.loading,
		latestForecast,
		latestTrappedLiquidity,
		hasActiveTrappedLiquidity,
		receivables.error,
		receivables.loading,
		runTrappedLiquidity,
		trappedLiquiditySimulations.error,
		trappedLiquiditySimulations.loading,
	]);

	useEffect(() => {
		if (
			!latestForecast ||
			forecasts.loading ||
			forecasts.error ||
			mitigationSimulations.loading ||
			mitigationSimulations.error ||
			latestMitigation ||
			hasActiveMitigation ||
			createLiquidityMitigation.pending ||
			createLiquidityMitigation.error ||
			initialMitigationForecast.current === latestForecast.id ||
			Number(latestForecast.predicted_net_cashflow) >=
				Number(latestForecast.solvency_buffer)
		) {
			return;
		}
		initialMitigationForecast.current = latestForecast.id;
		void runMitigation().catch(() => undefined);
	}, [
		activeMitigation,
		createLiquidityMitigation.error,
		createLiquidityMitigation.pending,
		forecasts.error,
		forecasts.loading,
		latestForecast,
		latestMitigation,
		hasActiveMitigation,
		mitigationSimulations.error,
		mitigationSimulations.loading,
		runMitigation,
	]);

	const resourceError =
		forecasts.error ??
		receivables.error ??
		(latestForecast
			? mitigationSimulations.error ?? trappedLiquiditySimulations.error
			: null);
	const noForecast =
		!forecasts.loading && !forecasts.error && latestForecast === null;
	const firstRunPending =
		(createLiquidityMitigation.pending && !mitigationResult) ||
		(createTrappedLiquidity.pending && !trappedLiquidityResult);
	const showSkeleton =
		!noForecast &&
		(forecasts.loading ||
			receivables.loading ||
			mitigationSimulations.loading ||
			trappedLiquiditySimulations.loading ||
			firstRunPending);
	const showEmpty =
		!showSkeleton &&
		!resourceError &&
		!noForecast &&
		Boolean(view) &&
		(view?.options.length ?? 0) === 0;

	const retry = () => {
		initialMitigationForecast.current = null;
		initialTrappedForecast.current = null;
		void forecasts.refresh();
		void receivables.refresh();
		void refreshMitigationSimulations();
		void refreshTrappedLiquiditySimulations();
	};

	return (
		<PageLayout title="Planning">
			<header>
				<p className="text-xs font-semibold uppercase tracking-widest text-primary">
					Planning
				</p>
				<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
					Planning
				</h1>
			<p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted sm:text-lg">
					Turn modeled signals into practical next steps without committing a
					financial action.
				</p>
			</header>

			{resourceError ? (
				<ResourceError
					title="Unable to load planning data"
					error={resourceError}
					onRetry={retry}
					className="mt-10"
				/>
			) : null}
			{createLiquidityMitigation.error ? (
				<InlineError className="mt-4">
					We couldn&apos;t prepare a cash plan. Please try again.
				</InlineError>
			) : null}
			{createTrappedLiquidity.error ? (
				<InlineError className="mt-2">
					We couldn&apos;t identify collection opportunities. Please try again.
				</InlineError>
			) : null}

			{noForecast ? (
				<section className="mt-14 rounded-card bg-primary-soft/50 p-6 sm:p-8">
					<h2 className="font-serif text-2xl text-ink">No planning result yet</h2>
					<p className="mt-2 max-w-xl text-sm leading-relaxed text-text-muted sm:text-base">
						Planning uses the latest completed forecast to identify practical cash
						actions. Run a forecast first, then return here to review the plan.
					</p>
					<a
						href="/forecast"
						className="mt-5 inline-flex text-sm font-medium text-primary underline-offset-4 hover:underline"
					>
						Open Forecast <span className="ml-2">→</span>
					</a>
				</section>
			) : null}

			{showSkeleton ? <PlanningSkeleton /> : null}

			{showEmpty ? (
				<section className="mt-14 rounded-card bg-primary-soft/50 p-6 sm:p-8">
					<h2 className="font-serif text-2xl text-ink">
						No recommended actions yet
					</h2>
					<p className="mt-2 max-w-xl text-sm leading-relaxed text-text-muted sm:text-base">
						The current forecast does not have a modeled collection opportunity or
						cash action that improves the outlook.
					</p>
				</section>
			) : null}

			{view && !showSkeleton && !noForecast && !showEmpty ? (
				<>
					<section
						className="mt-10 grid gap-5 lg:grid-cols-2"
						aria-label="Planning recommendations"
					>
						<RecommendationCard collection={view.collection} />
						<DraftScenarioCard draft={view.draft} />
					</section>

					<CashPosition
						baseline={view.baseline}
						buffer={view.buffer}
						draft={view.draft?.postScenario ?? null}
					/>

					<section
						id="mitigation-options"
						className="mt-12 sm:mt-14"
						aria-labelledby="mitigation-options-title"
					>
						<p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
							Ways to improve cash position
						</p>
						<p
							id="mitigation-options-title"
							className="mt-2 font-serif text-lg leading-tight text-ink sm:text-xl"
						>
							Cash impact spectrum
						</p>
						<div className="mt-10 lg:mt-6">
							<DesktopMitigationSpectrum options={view.options} />
							<MobileMitigationSpectrum options={view.options} />
						</div>
					</section>
				</>
			) : null}
		</PageLayout>
	);
}

export default PlanningPage;
