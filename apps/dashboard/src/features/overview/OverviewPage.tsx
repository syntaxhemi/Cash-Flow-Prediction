import { useCallback, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import type { ForecastRun as ApiForecastRun } from '@/api/contracts';
import PageLayout from '@/components/layout/PageLayout';
import Button from '@/components/ui/Button';
import InlineError from '@/components/ui/InlineError';
import ResourceError from '@/components/ui/ResourceError';
import { useEnterprise } from '@/hooks/useEnterprise';
import { useForecastMutations } from '@/hooks/useForecastMutations';
import { useForecasts } from '@/hooks/useForecasts';
import { useIngestionSources } from '@/hooks/useIngestionSources';
import { formatCurrency } from '@/utils/formatCurrency';
import DetailedForecastChart from '../forecast/DetailedForecastChart';
import { toForecastView } from '../forecast/adapters';
import type { Recommendation } from './types';
import EnterpriseContext from './EnterpriseContext';
import OverviewSkeleton from './OverviewSkeleton';
import RecommendationSequence from './RecommendationSequence';

function toApiDate(value: Date) {
	const month = String(value.getMonth() + 1).padStart(2, '0');
	const day = String(value.getDate()).padStart(2, '0');
	return `${value.getFullYear()}-${month}-${day}`;
}

function defaultForecastRange() {
	const startDate = new Date();
	startDate.setDate(1);
	const endDate = new Date(startDate);
	endDate.setDate(endDate.getDate() + 30);
	return { startDate, endDate };
}

function forecastDays(run: ApiForecastRun) {
	const start = Date.parse(`${run.target_period_start}T00:00:00`);
	const end = Date.parse(`${run.target_period_end}T00:00:00`);
	return Math.max(1, Math.round((end - start) / 86_400_000));
}

function recommendationsFor(run: ApiForecastRun): Recommendation[] {
	return (run.observation_drivers ?? []).slice(0, 3).map((driver, index) => ({
		number: String(index + 1).padStart(2, '0'),
		title: `Review ${driver.label}`,
		detail: driver.detail,
		action: 'Explore forecast',
		to: '/forecast',
		featured: index === 0,
	}));
}

function OverviewFirstRunState({
	hasSource,
	pending,
	error,
	onRun,
}: {
	hasSource: boolean;
	pending: boolean;
	error: Error | null;
	onRun: () => void;
}) {
	return (
		<section
			className="mt-12 rounded-card border border-primary/20 bg-primary-soft/35 p-6 sm:mt-16 sm:p-8"
			aria-labelledby="overview-first-run-title"
		>
			<p className="text-xs font-semibold uppercase tracking-widest text-primary">
				{hasSource ? 'Ready for your outlook' : 'Get started'}
			</p>
			<h2
				id="overview-first-run-title"
				className="mt-4 max-w-xl font-serif text-3xl leading-tight text-ink"
			>
				{hasSource
					? 'Your first forecast is ready to run.'
					: 'Connect financial data to generate your outlook.'}
			</h2>
			<p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted">
				{hasSource
					? 'We use the latest available records to prepare a 30-day baseline forecast.'
					: 'Once a source is connected, the dashboard will prepare a baseline forecast and highlight what needs attention.'}
			</p>
			{error ? <InlineError className="mt-4">{error.message}</InlineError> : null}
			{hasSource ? (
				<Button className="mt-6" onClick={onRun} disabled={pending}>
					{pending ? 'Running forecast...' : 'Run forecast'}
				</Button>
			) : (
				<Link
					to="/data"
					className="mt-6 inline-flex rounded-control bg-primary px-4 py-2.5 text-sm font-medium text-surface hover:bg-primary/90"
				>
					Connect data
				</Link>
			)}
		</section>
	);
}

function OverviewPage() {
	const { enterprise, enterpriseId, loading: enterpriseLoading, error: enterpriseError } =
		useEnterprise();
	const {
		data: sourcesData,
		loading: sourcesLoading,
		error: sourcesError,
		refresh: refreshSources,
	} = useIngestionSources(enterpriseId ?? undefined);
	const {
		data: forecastsData,
		loading: forecastsLoading,
		error: forecastsError,
		refresh: refreshForecasts,
	} = useForecasts(enterpriseId ?? undefined);
	const { createBaseline } = useForecastMutations(enterpriseId ?? undefined);
	const initialRunEnterprise = useRef<string | null>(null);
	const sourceItems = sourcesData?.items ?? [];
	const latestRun = forecastsData?.items[0] ?? null;
	const view = latestRun
		? toForecastView(latestRun, forecastsData?.items ?? [latestRun])
		: null;
	const hasSource = sourceItems.length > 0;

	const runForecast = useCallback(async () => {
		if (!enterpriseId) return;
		const { startDate, endDate } = defaultForecastRange();
		await createBaseline.mutateAsync({
			target_period_start: toApiDate(startDate),
			target_period_end: toApiDate(endDate),
			run_type: 'ad_hoc_baseline',
			solvency_buffer: latestRun?.solvency_buffer ?? 0,
		});
		await refreshForecasts();
	}, [createBaseline, enterpriseId, latestRun?.solvency_buffer, refreshForecasts]);

	useEffect(() => {
		if (
			!enterpriseId ||
			enterpriseLoading ||
			sourcesLoading ||
			forecastsLoading ||
			sourcesError ||
			forecastsError ||
			!sourcesData ||
			!forecastsData ||
			!hasSource ||
			forecastsData.items.length > 0 ||
			initialRunEnterprise.current === enterpriseId
		) {
			return;
		}

		initialRunEnterprise.current = enterpriseId;
		void runForecast().catch(() => undefined);
	}, [
		enterpriseId,
		enterpriseLoading,
		forecastsData,
		forecastsError,
		forecastsLoading,
		hasSource,
		runForecast,
		sourcesData,
		sourcesError,
		sourcesLoading,
	]);

	const resourceError = enterpriseError ?? sourcesError ?? forecastsError;
	const showSkeleton =
		enterpriseLoading ||
		sourcesLoading ||
		forecastsLoading ||
		(hasSource && !view && createBaseline.pending);
	const recommendations = latestRun ? recommendationsFor(latestRun) : [];

	return (
		<PageLayout title="Overview">
			{showSkeleton ? <OverviewSkeleton /> : null}
			{!showSkeleton ? (
				<>
					<EnterpriseContext
						enterpriseName={enterprise?.legal_name ?? 'Enterprise'}
						updatedAt={latestRun?.requested_at ?? null}
						hasForecast={Boolean(view)}
					/>

					{resourceError && !showSkeleton ? (
						<ResourceError
							title="Unable to load your outlook"
							error={resourceError}
							onRetry={() => {
								createBaseline.reset();
								void refreshSources();
								void refreshForecasts();
							}}
						/>
					) : null}

					{createBaseline.error && view && !createBaseline.pending ? (
						<InlineError className="mt-4">
							{createBaseline.error.message}
						</InlineError>
					) : null}

					{!resourceError && !view ? (
						<OverviewFirstRunState
							hasSource={hasSource}
							pending={createBaseline.pending}
							error={createBaseline.error}
							onRun={() => {
								void runForecast().catch(() => undefined);
							}}
						/>
					) : null}

					{view && latestRun ? (
						<>
							<section
								className="flex flex-col gap-10 lg:flex-row lg:items-center lg:gap-20"
								aria-labelledby="cash-position-title"
							>
								<div className="rounded-card bg-primary-soft/50 p-5 lg:rounded-none lg:bg-transparent lg:p-0">
									<p
										id="cash-position-title"
										className="text-xs font-semibold uppercase tracking-widest text-text-muted"
									>
										Projected net cash flow
									</p>
									<div className="mt-5 flex flex-wrap items-center gap-4">
										<p className="text-3xl font-medium tracking-tight text-ink sm:text-5xl lg:text-6xl">
											{formatCurrency(Number(latestRun.predicted_net_cashflow))}
										</p>
										<span
											className={`rounded-full px-3 py-1 text-xs font-medium sm:px-4 sm:py-2 sm:text-sm ${
												Number(latestRun.buffer_gap) >= 0
													? 'bg-primary text-surface'
													: 'bg-risk/10 text-risk'
											}`}
										>
											{Number(latestRun.buffer_gap) >= 0
												? 'Above buffer'
												: 'Below buffer'}
										</span>
									</div>
									<p className="mt-4 text-base text-text-muted">
										Projected net cash flow for the next {forecastDays(latestRun)} days.
									</p>
								</div>
								<p className="max-w-xl font-serif text-lg leading-tight text-ink sm:text-2xl">
									{latestRun.observations?.[0] ?? view.readout.description}
								</p>
							</section>

							<section className="mt-12 sm:mt-20" aria-labelledby="forecast-title">
								<div>
									<h2
										id="forecast-title"
										className="text-xs font-semibold uppercase tracking-widest text-text-muted sm:text-xl sm:font-medium sm:normal-case sm:tracking-tight sm:text-ink"
									>
										Cash flow outlook
									</h2>
									<p className="mt-2 text-sm text-text-muted">
										Historical performance and baseline forecast
									</p>
								</div>
								<div className="max-w-4xl pt-4">
									<DetailedForecastChart data={view.chart} />
								</div>
							</section>

							<div className="mt-12 flex flex-col gap-16 sm:mt-20 lg:flex-row lg:items-start lg:gap-12">
								<section className="relative lg:w-1/3" aria-labelledby="driver-title">
									<span
										className="absolute left-0 top-0 h-16 w-1 rounded-full bg-primary"
										aria-hidden="true"
									/>
									<div className="pl-6">
										<p className="text-xs font-semibold uppercase tracking-widest text-primary">
											Observation driver
										</p>
										<h2
											id="driver-title"
											className="mt-4 font-serif text-2xl leading-tight text-ink"
										>
											{latestRun.observation_drivers?.[0]?.label ??
												'No dominant driver identified'}
										</h2>
										<p className="mt-2 text-base text-text-muted">
											{latestRun.observation_drivers?.[0]?.detail ??
												'No observation driver was returned for this forecast.'}
										</p>
										<Link
											to="/forecast"
											className="mt-4 inline-flex border-b border-transparent pb-px text-sm font-medium text-primary no-underline hover:border-primary"
										>
											Open forecast <span className="ml-2" aria-hidden="true">→</span>
										</Link>
									</div>
								</section>

								{recommendations.length > 0 ? (
									<RecommendationSequence
										recommendations={recommendations}
										className="mt-0 lg:mt-0 lg:w-2/3"
									/>
								) : (
									<section className="lg:w-2/3" aria-labelledby="recommendations-title">
										<p
											id="recommendations-title"
											className="text-xs font-semibold uppercase tracking-widest text-primary"
										>
											Recommended next
										</p>
										<p className="mt-5 text-sm text-text-muted">
											No modeled next actions are available for this forecast yet.
										</p>
									</section>
								)}
							</div>
						</>
					) : null}
				</>
			) : null}
		</PageLayout>
	);
}

export default OverviewPage;
