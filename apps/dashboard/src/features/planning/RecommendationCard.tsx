import PlanningArrow from './PlanningArrow';

function RecommendationCard() {
	return (
		<article className="rounded-card border border-primary/20 bg-primary-soft/35 p-5 sm:p-6">
			<span className="inline-flex rounded-control border border-primary/20 bg-primary-soft px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-primary">
				Recommended next step
			</span>
			<p className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
				Draft recommendation
			</p>
			<h2 className="mt-2 max-w-xl font-serif text-xl leading-tight text-ink sm:text-2xl">
				Bring Apex Retail back to standard terms
			</h2>
			<p className="mt-3 max-w-xl text-sm leading-relaxed text-text-muted">
				Recovering the highest-impact customer balance would move the baseline
				toward the operating buffer.
			</p>
			<a
				href="/receivables"
				className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline"
			>
				View affected customer
				<PlanningArrow />
			</a>
		</article>
	);
}

export default RecommendationCard;
