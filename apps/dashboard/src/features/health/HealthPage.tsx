import { useCallback, useEffect, useRef, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import InlineError from '@/components/ui/InlineError';
import ResourceError from '@/components/ui/ResourceError';
import { useEnterprise } from '@/hooks/useEnterprise';
import { useForecastMutations } from '@/hooks/useForecastMutations';
import { useForecasts } from '@/hooks/useForecasts';
import { useSimulationResults } from '@/hooks/useSimulationResults';
import HealthFilterBar from './HealthFilterBar';
import HealthImpactCards from './HealthImpactCards';
import HealthPosition from './HealthPosition';
import HealthSkeleton from './HealthSkeleton';
import HealthStatsBar from './HealthStatsBar';
import { toHealthRequest, toHealthView } from './adapters';
import {
	healthScenarioInputs,
	healthScenarioOptions,
} from './scenario-options';
import type { HealthScenarioKey } from './types';

function HealthPage() {
	const { enterpriseId } = useEnterprise();
	const forecasts = useForecasts(
		enterpriseId ?? undefined,
		'ad_hoc_baseline',
		'completed',
		1,
		0,
	);
	const simulations = useSimulationResults(
		enterpriseId ?? undefined,
		'health_delta',
		'completed',
		undefined,
		undefined,
		100,
		0,
	);
	const { createHealthDelta } = useForecastMutations(enterpriseId ?? undefined);
	const [scenario, setScenario] = useState<HealthScenarioKey>('credit_score');
	const [scenarioValue, setScenarioValue] = useState(
		healthScenarioInputs.credit_score.defaultValue,
	);
	const [comparison, setComparison] = useState('baseline');
	const [activeSimulation, setActiveSimulation] = useState<Awaited<
		ReturnType<typeof createHealthDelta.mutateAsync>
	> | null>(null);
	const [selectionEdited, setSelectionEdited] = useState(false);
	const initialRunForecast = useRef<string | null>(null);
	const latestForecast = forecasts.data?.items[0] ?? null;
	const latestHealthSimulation = simulations.data?.find(
		(simulation) =>
			simulation.forecast_run_id === latestForecast?.id &&
			simulation.scenarios?.some((result) => result.health_score != null),
	);
	const baselineScenarioRaw = latestForecast?.static_snapshot?.[scenario];
	const baselineScenarioValue =
		baselineScenarioRaw === null || baselineScenarioRaw === undefined
			? Number.NaN
			: Number(baselineScenarioRaw);
	const configuredScenarioValue = Number.isFinite(baselineScenarioValue)
		? baselineScenarioValue
		: healthScenarioInputs[scenario].defaultValue;

	function configuredValueFor(nextScenario: HealthScenarioKey) {
		const rawValue = latestForecast?.static_snapshot?.[nextScenario];
		const value =
			rawValue === null || rawValue === undefined
				? Number.NaN
				: Number(rawValue);
		return Number.isFinite(value)
			? value
			: healthScenarioInputs[nextScenario].defaultValue;
	}
	const persistedResult = latestHealthSimulation?.scenarios?.find((result) =>
		healthScenarioOptions.some(
			(option) => result.input_patch_json[option.value] !== undefined,
		),
	);
	const persistedScenario = healthScenarioOptions.find(
		(option) => persistedResult?.input_patch_json[option.value] !== undefined,
	);
	const persistedValue = persistedScenario
		? Number(persistedResult?.input_patch_json[persistedScenario.value])
		: Number.NaN;
	const effectiveScenario =
		!selectionEdited && !activeSimulation && persistedScenario
			? (persistedScenario.value as HealthScenarioKey)
			: scenario;
	const effectiveScenarioValue =
		!selectionEdited && !activeSimulation
			? Number.isFinite(persistedValue)
				? persistedValue
				: configuredScenarioValue
			: scenarioValue;

	const runScenario = useCallback(async () => {
		if (!latestForecast) {
			throw new Error(
				'A completed forecast is required before running a scenario.',
			);
		}

		const result = await createHealthDelta.mutateAsync({
			forecastRunId: latestForecast.id,
			body: toHealthRequest(effectiveScenario, effectiveScenarioValue),
		});
		setActiveSimulation(result);
		void simulations.refresh();
	}, [
		createHealthDelta,
		effectiveScenario,
		effectiveScenarioValue,
		latestForecast,
		simulations,
	]);

	useEffect(() => {
		if (
			!latestForecast ||
			forecasts.loading ||
			forecasts.error ||
			simulations.loading ||
			simulations.error ||
			latestHealthSimulation ||
			activeSimulation ||
			selectionEdited ||
			createHealthDelta.pending ||
			createHealthDelta.error ||
			initialRunForecast.current === latestForecast.id
		) {
			return;
		}

		initialRunForecast.current = latestForecast.id;
		void runScenario().catch(() => undefined);
	}, [
		activeSimulation,
		createHealthDelta.error,
		createHealthDelta.pending,
		forecasts.error,
		forecasts.loading,
		latestForecast,
		latestHealthSimulation,
		runScenario,
		selectionEdited,
		simulations.error,
		simulations.loading,
	]);

	const resultSimulation = activeSimulation ?? latestHealthSimulation;
	const resultScenario = activeSimulation
		? effectiveScenario
		: (persistedScenario?.value as HealthScenarioKey | undefined) ??
			effectiveScenario;
	const view =
		latestForecast && resultSimulation
			? toHealthView(
					resultSimulation,
					Number(latestForecast.predicted_net_cashflow),
					resultScenario,
					latestForecast.observation_drivers,
				)
			: null;
	const resourceError = forecasts.error ?? simulations.error;
	const showSkeleton =
		forecasts.loading ||
		simulations.loading ||
		(Boolean(latestForecast) &&
			!view &&
			!resourceError &&
			!createHealthDelta.error);
	const showNoForecast =
		!forecasts.loading &&
		!simulations.loading &&
		!resourceError &&
		!latestForecast;
	const showNoScenarioResult =
		Boolean(latestForecast) &&
		!view &&
		!showSkeleton &&
		!resourceError &&
		!createHealthDelta.error;

	return (
		<PageLayout title="Health">
			<header>
				<p className="text-xs font-semibold uppercase tracking-widest text-primary">
					Health &amp; sensitivity
				</p>
				<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
					Health
				</h1>
				<p className="mt-4 max-w-2xl text-base text-text-muted sm:text-lg">
					See how changes in key drivers impact your cash position and health.
				</p>
			</header>

			<HealthFilterBar
				scenario={effectiveScenario}
				scenarioValue={effectiveScenarioValue}
				comparison={comparison}
				pending={createHealthDelta.pending}
				disabled={!latestForecast || forecasts.loading || !!resourceError}
				onScenarioChange={(nextScenario) => {
					setSelectionEdited(true);
					setScenario(nextScenario);
					setScenarioValue(configuredValueFor(nextScenario));
				}}
				onScenarioValueChange={(value) => {
					setSelectionEdited(true);
					setScenarioValue(value);
				}}
				onComparisonChange={setComparison}
				onRun={() => {
					void runScenario().catch(() => undefined);
				}}
			/>

			{resourceError && !showSkeleton ? (
				<ResourceError
					title="Unable to load health data"
					error={resourceError}
					onRetry={() => {
						createHealthDelta.reset();
						void forecasts.refresh();
						void simulations.refresh();
					}}
					className="mt-10"
				/>
			) : null}
			{createHealthDelta.error && !createHealthDelta.pending ? (
				<InlineError className="mt-4">
					{createHealthDelta.error.message}
				</InlineError>
			) : null}

			{showNoForecast ? (
				<section
					className="mt-14 rounded-card bg-primary-soft/50 p-6 sm:p-8"
					aria-label="No completed forecast"
				>
					<h2 className="font-serif text-2xl text-ink">No health result yet</h2>
					<p className="mt-2 max-w-xl text-sm leading-relaxed text-text-muted sm:text-base">
						Health scenarios use the latest completed forecast. Run a forecast
						first, then return here to explore supported model drivers.
					</p>
					<a
						href="/forecast"
						className="mt-5 inline-flex text-sm font-medium text-primary underline-offset-4 hover:underline"
					>
						Open Forecast{' '}
						<span className="ml-2" aria-hidden="true">
							→
						</span>
					</a>
				</section>
			) : null}
			{showNoScenarioResult ? (
				<p className="mt-14 text-sm text-text-muted">
					Run the selected scenario to see its health and cash-flow impact.
				</p>
			) : null}

			{showSkeleton ? <HealthSkeleton /> : null}

			{view ? (
				<>
					<HealthStatsBar stats={view.stats} />
					<div className="mt-16 flex flex-col gap-16 sm:mt-20 sm:gap-20 lg:mt-16 lg:flex-row lg:items-start lg:gap-12 xl:gap-16">
						<HealthPosition
							scores={view.scores}
							healthDelta={view.healthDelta}
							healthDeltaValue={view.healthDeltaValue}
							className="mt-0 lg:mt-0 lg:w-1/2"
						/>
						<HealthImpactCards
							impacts={view.impacts}
							className="mt-0 lg:mt-0 lg:w-1/2"
						/>
					</div>
				</>
			) : null}

			<p className="mt-12 text-xs text-text-muted sm:mt-16">
				Modeled result — directional decision support, not a covenant-compliance
				determination.
			</p>
		</PageLayout>
	);
}

export default HealthPage;
