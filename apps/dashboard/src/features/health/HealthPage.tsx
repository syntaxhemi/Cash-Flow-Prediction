import PageLayout from '@/components/layout/PageLayout';
import HealthFilterBar from './HealthFilterBar';
import HealthImpactCards from './HealthImpactCards';
import HealthPosition from './HealthPosition';
import HealthStatsBar from './HealthStatsBar';
import { healthMockData } from './mock-data';

function HealthPage() {
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

			<HealthFilterBar />
			<HealthStatsBar stats={healthMockData.stats} />
			<div className="mt-16 flex flex-col gap-16 sm:mt-20 sm:gap-20 lg:mt-16 lg:flex-row lg:items-start lg:gap-12 xl:gap-16">
				<HealthPosition
					scores={healthMockData.scores}
					healthDelta={healthMockData.healthDelta}
					className="mt-0 lg:mt-0 lg:w-1/2"
				/>
				<HealthImpactCards
					impacts={healthMockData.impacts}
					className="mt-0 lg:mt-0 lg:w-1/2"
				/>
			</div>

			<p className="mt-12 text-xs text-text-muted sm:mt-16">
				Modeled result — directional decision support, not a covenant-compliance
				determination.
			</p>
		</PageLayout>
	);
}

export default HealthPage;
