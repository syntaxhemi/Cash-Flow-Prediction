import PlanningArrow from './PlanningArrow';
import type { PlanningCollectionOpportunity } from './types';

type RecommendationCardProps = {
	collection: PlanningCollectionOpportunity | null;
};

function RecommendationCard({ collection }: RecommendationCardProps) {
	const name = collection?.name ?? 'the highest-impact receivable';
	const title = collection
		? `Bring ${name} closer to expected payment timing`
		: 'Review the highest-impact cash action';
	return (
		<article className="rounded-card border border-primary/20 bg-primary-soft/35 p-5 sm:p-6">
			<span className="inline-flex rounded-control border border-primary/20 bg-primary-soft px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-primary">
				Recommended next step
			</span>
			<p className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
				Draft recommendation
			</p>
			<h2 className="mt-2 max-w-xl font-serif text-xl leading-tight text-ink sm:text-2xl">
				{title}
			</h2>
			<p className="mt-3 max-w-xl text-sm leading-relaxed text-text-muted">
				{collection
					? 'Collecting the highest-impact open balance could improve the modeled cash position without committing an accounting action.'
					: 'The strongest available cash action could improve the modeled cash position without committing an accounting action.'}
			</p>
			<a
				href={collection?.linkHref ?? '/receivables'}
				className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline"
			>
				View affected customer
				<PlanningArrow />
			</a>
		</article>
	);
}

export default RecommendationCard;
