import PageLayout from '@/components/layout/PageLayout';
import CashPosition from './CashPosition';
import DraftScenarioCard from './DraftScenarioCard';
import {
	DesktopMitigationSpectrum,
	MobileMitigationSpectrum,
} from './MitigationSpectrum';
import { mitigationOptions } from './mock-data';
import RecommendationCard from './RecommendationCard';

function PlanningPage() {
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
					Turn modeled signals into bounded next steps without committing a
					financial action.
				</p>
			</header>

			<section
				className="mt-10 grid gap-5 lg:grid-cols-2"
				aria-label="Planning recommendations"
			>
				<RecommendationCard />
				<DraftScenarioCard />
			</section>

			<CashPosition />

			<section
				id="mitigation-options"
				className="mt-12 sm:mt-14"
				aria-labelledby="mitigation-options-title"
			>
				<p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
					Mitigation options
				</p>
				<p
					id="mitigation-options-title"
					className="mt-2 font-serif text-lg leading-tight text-ink sm:text-xl"
				>
					Cash impact spectrum
				</p>
				<div className="mt-10 lg:mt-6">
					<DesktopMitigationSpectrum options={mitigationOptions} />
					<MobileMitigationSpectrum options={mitigationOptions} />
				</div>
			</section>
		</PageLayout>
	);
}

export default PlanningPage;
