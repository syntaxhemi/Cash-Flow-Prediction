import PageLayout from '@/components/layout/PageLayout';
import InlineError from '@/components/ui/InlineError';
import ResourceError from '@/components/ui/ResourceError';
import { useCallback, useEffect, useRef } from 'react';
import { useEnterprise } from '@/hooks/useEnterprise';
import { useForecastMutations } from '@/hooks/useForecastMutations';
import { useForecasts } from '@/hooks/useForecasts';
import CashMovement from './CashMovement';
import ForecastChart from './DetailedForecastChart';
import ForecastFilterBar from './ForecastFilterBar';
import ForecastImpactGrid from './ForecastImpactGrid';
import ForecastReadout from './ForecastReadout';
import ForecastRuns from './ForecastRuns';
import ForecastSkeleton from './ForecastSkeleton';
import { toForecastView } from './adapters';
import type { ForecastRange } from './ForecastFilterBar';

function ForecastPage() {
	const { enterpriseId } = useEnterprise();
	const forecasts = useForecasts(enterpriseId ?? undefined);
	const { createBaseline } = useForecastMutations(enterpriseId ?? undefined);
	const {
		data: forecastData,
		loading: forecastsLoading,
		error: forecastsError,
		refresh: refreshForecasts,
	} = forecasts;
	const latestRun = forecastData?.items[0] ?? null;
	const initialRunEnterprise = useRef<string | null>(null);
	const view = latestRun
		? toForecastView(latestRun, forecastData?.items ?? [latestRun])
		: null;
	const showForecastSkeleton =
		forecastsLoading || (!forecastsError && !view && createBaseline.pending);

	const toApiDate = (value: Date) => {
		const month = String(value.getMonth() + 1).padStart(2, '0');
		const day = String(value.getDate()).padStart(2, '0');
		return `${value.getFullYear()}-${month}-${day}`;
	};

	const runForecast = useCallback(
		async ({ startDate, endDate }: ForecastRange) => {
			await createBaseline.mutateAsync({
				target_period_start: toApiDate(startDate),
				target_period_end: toApiDate(endDate),
				run_type: 'ad_hoc_baseline',
				solvency_buffer: latestRun?.solvency_buffer ?? 0,
			});
			await refreshForecasts();
		},
		[createBaseline, latestRun?.solvency_buffer, refreshForecasts],
	);

	useEffect(() => {
		if (
			!enterpriseId ||
			forecastsLoading ||
			forecastsError ||
			forecastData === null ||
			forecastData.items.length > 0 ||
			initialRunEnterprise.current === enterpriseId
		) {
			return;
		}

		initialRunEnterprise.current = enterpriseId;
		const startDate = new Date();
		startDate.setDate(1);
		const endDate = new Date(startDate);
		endDate.setDate(endDate.getDate() + 30);
		void runForecast({ startDate, endDate }).catch(() => undefined);
	}, [
		enterpriseId,
		forecastData,
		forecastsError,
		forecastsLoading,
		runForecast,
	]);

	return (
		<PageLayout title="Forecast">
			<header>
				<p className="text-xs font-semibold uppercase tracking-widest text-primary">
					Forecast workspace
				</p>
				<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
					Forecast
				</h1>
				<p className="mt-4 max-w-2xl text-base text-text-muted sm:text-lg">
					Shape the horizon, compare scenarios, and understand what moves cash.
				</p>
			</header>

			<ForecastFilterBar
				pending={createBaseline.pending}
				disabled={!enterpriseId}
				onRun={(range) => {
					void runForecast(range).catch(() => undefined);
				}}
			/>

			{showForecastSkeleton ? <ForecastSkeleton /> : null}
			{forecastsError && !showForecastSkeleton ? (
				<ResourceError
					title="Unable to load forecast data"
					error={forecastsError}
					onRetry={() => {
						createBaseline.reset();
						void refreshForecasts();
					}}
					className="mt-10"
				/>
			) : null}
			{createBaseline.error && !createBaseline.pending ? (
				<InlineError className="mt-4">
					{createBaseline.error.message}
				</InlineError>
			) : null}

			{!showForecastSkeleton &&
			!forecastsLoading &&
			!forecastsError &&
			!createBaseline.error &&
			!view ? (
				<p className="mt-10 text-sm text-text-muted">
					No forecast runs are available yet.
				</p>
			) : null}

			{view ? (
				<section className="mt-16 lg:mt-24" aria-label="Baseline forecast">
					<div className="lg:grid lg:grid-cols-[minmax(0,2.2fr)_minmax(20rem,1fr)] lg:items-start">
						<div>
							<ForecastChart data={view.chart} />
						</div>
						<ForecastReadout {...view.readout} />
					</div>
				</section>
			) : null}

			{view ? (
				<div className="mt-20 grid gap-16 lg:mt-24 lg:grid-cols-2 lg:gap-20">
					<CashMovement {...view.cashMovement} />
					<ForecastImpactGrid impacts={view.impacts} />
				</div>
			) : null}

			{view ? (
				<div className="mt-16 lg:mt-20">
					<ForecastRuns
						runs={view.runs}
						baselineSnapshot={view.baselineSnapshot}
					/>
				</div>
			) : null}
		</PageLayout>
	);
}

export default ForecastPage;
