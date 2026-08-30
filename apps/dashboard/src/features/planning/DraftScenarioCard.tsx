import Button from '@/components/ui/Button';

function DraftScenarioCard() {
	return (
		<article className="rounded-card border border-simulation/20 bg-[#fbf8fc] p-5 sm:p-6">
			<span className="inline-flex rounded-control border border-simulation/20 bg-[#f2edf1] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-simulation">
				Draft scenario
			</span>
			<h2 className="mt-4 font-serif text-xl leading-tight text-ink sm:text-2xl">
				Apex Retail collection timing
			</h2>
			<div className="mt-4 grid gap-5 lg:grid-cols-[minmax(0,1fr)_12rem] lg:items-center lg:gap-6">
				<div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-start gap-3 sm:gap-5">
					<div className="min-w-0">
						<p className="text-xs text-text-muted">Current</p>
						<p className="mt-1 font-serif text-sm leading-tight text-ink lg:text-xl">
							12 days overdue
						</p>
					</div>
					<span
						className="mt-5 pb-0.5 text-xl text-simulation"
						aria-hidden="true"
					>
						→
					</span>
					<div className="min-w-0">
						<p className="text-xs text-text-muted">Proposed</p>
						<p className="mt-1 font-serif text-sm leading-tight text-ink lg:text-xl">
							On standard terms
						</p>
					</div>
				</div>
				<div className="flex flex-col gap-3 border-t border-border/80 pt-4 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
					<Button variant="soft" size="sm" className="w-full lg:w-auto">
						Adjust draft
					</Button>
					<p className="text-sm leading-relaxed text-text-muted">
						No accounting action has been committed.
					</p>
				</div>
			</div>
		</article>
	);
}

export default DraftScenarioCard;
