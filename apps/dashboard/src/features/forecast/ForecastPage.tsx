import PageLayout from '@/components/layout/PageLayout';
import CashMovement from './CashMovement';
import ForecastChart from './DetailedForecastChart';
import ForecastFilterBar from './ForecastFilterBar';
import ForecastImpactGrid from './ForecastImpactGrid';
import ForecastReadout from './ForecastReadout';
import ForecastRuns from './ForecastRuns';
import { forecastMockData } from './mock-data';

function ForecastPage() {
	const { chart, impacts, runs, baselineSnapshot } = forecastMockData;

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

			<ForecastFilterBar />

			<section className="mt-16 lg:mt-24" aria-label="Baseline forecast">
				<div className="lg:grid lg:grid-cols-[minmax(0,2.2fr)_minmax(20rem,1fr)] lg:items-start">
					<div>
						<ForecastChart data={chart} />
					</div>
					<ForecastReadout />
				</div>
			</section>

			<div className="mt-20 grid gap-16 lg:mt-24 lg:grid-cols-2 lg:gap-20">
				<CashMovement />
				<ForecastImpactGrid impacts={impacts} />
			</div>

			<div className="mt-16 lg:mt-20">
				<ForecastRuns runs={runs} baselineSnapshot={baselineSnapshot} />
			</div>
		</PageLayout>
	);
}

export default ForecastPage;
