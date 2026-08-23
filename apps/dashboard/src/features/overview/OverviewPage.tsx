import PageLayout from '@/components/layout/PageLayout';
import { formatCurrency } from '@/utils/formatCurrency';
import EnterpriseContext from './EnterpriseContext';
import ForecastChart from './ForecastChart';
import { overviewMockData } from './mock-data';
import RecommendationSequence from './RecommendationSequence';

function OverviewPage() {
	const {
		cashPosition,
		status,
		projectionDescription,
		insight,
		forecastChart,
		driver,
		recommendations,
	} = overviewMockData;

	return (
		<PageLayout title="Overview">
			<EnterpriseContext />
			<section
				className="flex flex-col gap-10 lg:flex-row lg:items-center lg:gap-20"
				aria-labelledby="cash-position-title"
			>
				<div className="rounded-card bg-primary-soft/50 p-5 lg:rounded-none lg:bg-transparent lg:p-0">
					<p
						id="cash-position-title"
						className="text-xs font-semibold uppercase tracking-widest text-text-muted"
					>
						Cash position at a glance
					</p>
					<div className="mt-5 flex flex-wrap items-center gap-4">
						<p className="text-3xl font-medium tracking-tight text-ink sm:text-5xl lg:text-6xl">
							{formatCurrency(cashPosition)}
						</p>
						<span className="rounded-full bg-primary px-3 py-1 text-xs font-medium text-surface sm:px-4 sm:py-2 sm:text-sm">
							{status}
						</span>
					</div>
					<p className="mt-4 text-base text-text-muted">
						{projectionDescription}
					</p>
				</div>
				<p className="max-w-xl font-serif text-lg leading-tight text-ink sm:text-2xl">
					{insight}
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
				<ForecastChart data={forecastChart} />
			</section>

			<div className="mt-12 flex flex-col gap-16 sm:mt-20 lg:flex-row lg:items-start lg:gap-12">
				<section className="relative lg:w-1/3" aria-labelledby="driver-title">
					<span
						className="absolute left-0 top-0 h-16 w-1 rounded-full bg-primary"
						aria-hidden="true"
					/>
					<div className="pl-6">
						<p className="text-xs font-semibold uppercase tracking-widest text-primary">
							{driver.label}
						</p>
						<h2
							id="driver-title"
							className="mt-4 font-serif text-2xl leading-tight text-ink"
						>
							{driver.title}
						</h2>
						<p className="mt-2 text-base text-text-muted">{driver.corollary}</p>
						<a
							href={driver.to}
							className="mt-4 inline-flex border-b border-transparent pb-px text-sm font-medium text-primary no-underline hover:border-primary"
						>
							<span>
								{driver.linkLabel}{' '}
								<span className="ml-2" aria-hidden="true">
									→
								</span>
							</span>
						</a>
					</div>
				</section>

				<RecommendationSequence
					recommendations={recommendations}
					className="mt-0 lg:mt-0 lg:w-2/3"
				/>
			</div>
		</PageLayout>
	);
}

export default OverviewPage;
