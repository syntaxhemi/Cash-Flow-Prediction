import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { LuArrowUpRight } from 'react-icons/lu';
import type { SimulationRun } from '@/api/contracts';
import PageLayout from '@/components/layout/PageLayout';
import InlineError from '@/components/ui/InlineError';
import ResourceError from '@/components/ui/ResourceError';
import { useEnterprise } from '@/hooks/useEnterprise';
import { useForecastMutations } from '@/hooks/useForecastMutations';
import { useForecasts } from '@/hooks/useForecasts';
import { useReceivables } from '@/hooks/useReceivables';
import { useSimulationResults } from '@/hooks/useSimulationResults';
import { formatCurrency } from '@/utils/formatCurrency';
import ImpactRanking from './ImpactRanking';
import { toReceivablesView } from './adapters';
import { horizonOptions } from './options';
import ReceivablesControls from './ReceivablesControls';
import ReceivablesSkeleton from './ReceivablesSkeleton';
import SupportingRecords from './SupportingRecords';

type Horizon = (typeof horizonOptions)[number]['value'];

function ReceivablesPage() {
	const { enterpriseId } = useEnterprise();
	const forecasts = useForecasts(
		enterpriseId ?? undefined,
		'ad_hoc_baseline',
		'completed',
		1,
		0,
	);
	const latestForecast = forecasts.data?.items[0] ?? null;
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [horizon, setHorizon] = useState<Horizon>('30');
	const [sortBy, setSortBy] = useState('impact');
	const [accountFilter, setAccountFilter] = useState('all');
	const [delayDays, setDelayDays] = useState(4);
	const [activeSimulation, setActiveSimulation] = useState<SimulationRun | null>(
		null,
	);
	const [previewSimulation, setPreviewSimulation] =
		useState<SimulationRun | null>(null);
	const initialRunForecast = useRef<string | null>(null);
	const simulations = useSimulationResults(
		enterpriseId ?? undefined,
		'trapped_liquidity',
		'completed',
		undefined,
		undefined,
		100,
		0,
	);
	const { refresh: refreshSimulations } = simulations;
	const { createTrappedLiquidity } = useForecastMutations(
		enterpriseId ?? undefined,
	);
	const receivableParams = useMemo(
		() =>
			latestForecast
				? {
						forecast_run_id: latestForecast.id,
						account_filter: accountFilter as 'all' | 'overdue' | 'upcoming',
						horizon_days: Number(horizon) as 30 | 60 | 90,
					}
				: null,
		[accountFilter, horizon, latestForecast],
	);
	const receivables = useReceivables(enterpriseId ?? undefined, receivableParams);
	const latestSimulation = simulations.data?.find(
		(simulation) =>
			simulation.forecast_run_id === latestForecast?.id &&
			simulation.summary_result?.run_purpose !== 'preview',
	);
	const view = receivables.data
		? toReceivablesView(
				receivables.data,
				activeSimulation ?? latestSimulation ?? null,
			)
		: null;
	const initialAnalysisPending =
		createTrappedLiquidity.pending && !activeSimulation && !latestSimulation;
	const sortedReceivables = useMemo(() => {
		if (!view) return [];
		return [...view.items].sort((left, right) => {
			if (sortBy === 'amount') return right.outstanding - left.outstanding;
			if (sortBy === 'delay')
				return (right.medianDays ?? 0) - (left.medianDays ?? 0);
			return Math.abs(right.predictedDelta) - Math.abs(left.predictedDelta);
		});
	}, [sortBy, view]);
	const selectedReceivable =
		sortedReceivables.find((receivable) => receivable.id === selectedId) ??
		sortedReceivables[0] ??
		null;
	const maximumImpact = Math.max(
		1,
		...sortedReceivables.map((receivable) =>
			Math.abs(receivable.predictedDelta),
		),
	);

	const runAnalysis = useCallback(async () => {
		if (!latestForecast) {
			throw new Error(
				'A completed forecast is required before running receivables analysis.',
			);
		}
		const result = await createTrappedLiquidity.mutateAsync({
			forecastRunId: latestForecast.id,
			body: { counterparty_ids: null, max_counterparties: 50 },
		});
		setActiveSimulation(result);
		setPreviewSimulation(null);
		void refreshSimulations();
	}, [createTrappedLiquidity, latestForecast, refreshSimulations]);

	useEffect(() => {
		if (
			!latestForecast ||
			forecasts.loading ||
			forecasts.error ||
			receivables.loading ||
			receivables.error ||
			simulations.loading ||
			simulations.error ||
			latestSimulation ||
			activeSimulation ||
			createTrappedLiquidity.pending ||
			createTrappedLiquidity.error ||
			initialRunForecast.current === latestForecast.id
		)
			return;
		initialRunForecast.current = latestForecast.id;
		void runAnalysis().catch(() => undefined);
	}, [
		activeSimulation,
		createTrappedLiquidity.error,
		createTrappedLiquidity.pending,
		forecasts.error,
		forecasts.loading,
		latestForecast,
		latestSimulation,
		receivables.error,
		receivables.loading,
		runAnalysis,
		simulations.error,
		simulations.loading,
		initialRunForecast,
	]);

	const previewImpact = useCallback(async () => {
		if (!latestForecast || !selectedReceivable) return;
		const result = await createTrappedLiquidity.mutateAsync({
			forecastRunId: latestForecast.id,
			body: {
				counterparty_ids: [selectedReceivable.id],
				max_counterparties: 1,
				payment_delay_days: delayDays,
			},
		});
		setPreviewSimulation(result);
	}, [createTrappedLiquidity, delayDays, latestForecast, selectedReceivable]);

	const resourceError =
		forecasts.error ?? receivables.error ?? simulations.error;
	const showNoForecast =
		!forecasts.loading && !forecasts.error && !latestForecast;
	const showNoReceivables =
		!forecasts.loading &&
		!receivables.loading &&
		!resourceError &&
		Boolean(latestForecast) &&
		view?.items.length === 0;
	const showSkeleton =
		forecasts.loading ||
		receivables.loading ||
		(simulations.loading && !activeSimulation) ||
		initialAnalysisPending ||
		(Boolean(latestForecast) && !view && !resourceError);

	const topReceivable = sortedReceivables[0] ?? null;

	return (
		<PageLayout title="Receivables">
			<header>
				<p className="text-xs font-semibold uppercase tracking-widest text-primary">
					Receivables &amp; trapped liquidity
				</p>
				<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
					Receivables
				</h1>
				<p className="mt-4 max-w-2xl text-base text-text-muted sm:text-lg">
					Prioritize the customers whose payment timing could change your
					near-term cash outlook.
				</p>
			</header>

			<ReceivablesControls
				horizon={horizon}
				onHorizonChange={setHorizon}
				sortBy={sortBy}
				onSortChange={setSortBy}
				accountFilter={accountFilter}
				onAccountFilterChange={setAccountFilter}
				pending={createTrappedLiquidity.pending}
				disabled={!latestForecast || Boolean(resourceError)}
				onRun={() => {
					void runAnalysis().catch(() => undefined);
				}}
			/>

			{resourceError ? (
				<ResourceError
					title="Unable to load receivables"
					error={resourceError}
					onRetry={() => {
						void forecasts.refresh();
						void receivables.refresh();
						void simulations.refresh();
					}}
					className="mt-10"
				/>
			) : null}
			{createTrappedLiquidity.error ? (
				<InlineError className="mt-4">
					{createTrappedLiquidity.error.message}
				</InlineError>
			) : null}

			{showNoForecast ? (
				<section className="mt-14 rounded-card bg-primary-soft/50 p-6 sm:p-8">
					<h2 className="font-serif text-2xl text-ink">
						No receivables analysis yet
					</h2>
					<p className="mt-2 max-w-xl text-sm leading-relaxed text-text-muted sm:text-base">
						Receivables analysis uses the latest completed forecast. Run a forecast
						first, then return here to inspect modeled payment timing impact.
					</p>
					<a
						href="/forecast"
						className="mt-5 inline-flex text-sm font-medium text-primary underline-offset-4 hover:underline"
					>
						Open Forecast <span className="ml-2">→</span>
					</a>
				</section>
			) : null}
			{showSkeleton ? (
				<ReceivablesSkeleton />
			) : null}
			{showNoReceivables ? (
				<p className="mt-14 text-sm text-text-muted">
					No open receivables match the selected view.
				</p>
			) : null}

			{view && !showNoReceivables ? (
				<>
					<section
						className="mt-14 grid gap-12 lg:grid-cols-[minmax(0,1.25fr)_minmax(20rem,0.75fr)] lg:items-start lg:gap-20"
						aria-label="Receivables summary"
					>
						<article className="rounded-card bg-primary-soft p-6 sm:p-8">
							<p className="text-xs font-semibold uppercase tracking-widest text-primary">
								Cash tied up in late payments
							</p>
							<div className="mt-4 flex flex-wrap items-baseline gap-x-4 gap-y-2">
								<p className="text-4xl font-medium tracking-tight text-primary sm:text-5xl">
									{formatCurrency(view.summary.modeledTrappedLiquidity)}
								</p>
								<span className="text-sm text-text-muted">
									across {view.summary.counterpartyCount} customers
								</span>
							</div>
							<p className="mt-4 max-w-xl text-sm leading-relaxed text-ink sm:text-base">
								Modeled cash that could return to the forecast if ranked customers
								paid on schedule.
							</p>
							<div className="mt-8 grid max-w-xl grid-cols-2 gap-6 pt-1">
								<div>
									<p className="text-xs text-text-muted">Open balance</p>
									<p className="mt-1 text-xl tabular-nums text-ink">
										{formatCurrency(view.summary.totalOutstanding)}
									</p>
								</div>
								<div>
									<p className="text-xs text-text-muted">Median payment</p>
									<p className="mt-1 text-xl tabular-nums text-ink">
										{view.summary.medianDays === null
											? '—'
											: `${view.summary.medianDays} days`}
									</p>
								</div>
							</div>
						</article>
						<div className="pt-1 lg:pt-6">
							<p className="text-xs font-semibold uppercase tracking-widest text-primary">
								Collection opportunity
							</p>
							<h2 className="mt-4 max-w-md font-serif text-2xl leading-tight text-ink sm:text-3xl">
								{topReceivable
									? `${topReceivable.name} is the clearest near-term collection opportunity.`
									: 'No ranked collection opportunity yet.'}
							</h2>
							<p className="mt-3 max-w-md text-sm leading-relaxed text-text-muted sm:text-base">
								{topReceivable
									? `Rank #${topReceivable.rank ?? '—'} has ${formatCurrency(Math.abs(topReceivable.predictedDelta))} of modeled cash-flow opportunity and ${topReceivable.medianDays ?? '—'} days typical payment delay.`
									: 'Run the analysis to rank customers by modeled cash-flow opportunity.'}
							</p>
							<a
								href="#customer-detail-desktop"
								className="mt-5 hidden items-center gap-2 text-sm font-medium text-primary no-underline hover:underline lg:inline-flex"
							>
								Inspect the top-ranked customer <LuArrowUpRight className="size-4" />
							</a>
							<a
								href="#customer-detail-mobile"
								className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline lg:hidden"
							>
								Inspect the top-ranked customer <LuArrowUpRight className="size-4" />
							</a>
						</div>
					</section>

					{selectedReceivable ? (
					<ImpactRanking
						receivables={sortedReceivables}
						selectedReceivable={selectedReceivable}
						maximumImpact={maximumImpact}
						onSelect={(id) => {
							setSelectedId(id);
							setPreviewSimulation(null);
						}}
						delayDays={delayDays}
						onDelayChange={setDelayDays}
						simulationRun={previewSimulation !== null}
						onPreview={() => {
							void previewImpact().catch(() => undefined);
						}}
						previewPending={createTrappedLiquidity.pending}
						previewSimulation={previewSimulation}
						visibleCount={sortedReceivables.length}
						counterpartyCount={view.summary.counterpartyCount}
						horizon={horizon}
					/>
					) : null}
					{selectedReceivable ? (
						<SupportingRecords receivable={selectedReceivable} />
					) : null}
				</>
			) : null}
			<p className="mt-10 text-xs leading-relaxed text-text-muted">
				Estimates on this page show how payment timing could affect the baseline
				forecast. They are decision support, not a confirmed collection outcome.
			</p>
		</PageLayout>
	);
}

export default ReceivablesPage;
