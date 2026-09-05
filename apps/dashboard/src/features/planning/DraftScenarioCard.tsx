import type { PlanningDraft } from './types';
import { formatAmount } from './adapters';

type DraftScenarioCardProps = { draft: PlanningDraft | null };

function DraftScenarioCard({ draft }: DraftScenarioCardProps) {
	return (
		<article className="rounded-card border border-simulation/20 bg-[#fbf8fc] p-5 sm:p-6">
			<span className="inline-flex rounded-control border border-simulation/20 bg-[#f2edf1] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-simulation">
				Draft scenario
			</span>
			<h2 className="mt-4 font-serif text-xl leading-tight text-ink sm:text-2xl">
				{draft?.name ?? 'No draft action available'}
			</h2>
			<div className="mt-4 grid gap-5 lg:grid-cols-[minmax(0,1fr)_12rem] lg:items-center lg:gap-6">
				<div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-start gap-3 sm:gap-5">
					<div className="min-w-0">
						<p className="text-xs text-text-muted">Current</p>
						<p className="mt-1 font-serif text-sm leading-tight text-ink lg:text-xl">
							{draft?.current ?? 'Run a completed forecast first'}
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
							{draft?.proposed ?? 'No action available yet'}
						</p>
					</div>
				</div>
				<div className="flex flex-col gap-3 border-t border-border/80 pt-4 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
					<a
						href={draft?.linkHref ?? '#mitigation-options'}
						className="inline-flex min-h-8 w-full items-center justify-center rounded-pill border border-primary-soft bg-primary-soft px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:border-primary lg:w-auto"
					>
						Review this plan
					</a>
					<p className="text-sm leading-relaxed text-text-muted">
						Modeled impact:{' '}
						{draft
							? `${draft.impact >= 0 ? '+' : '−'}${formatAmount(Math.abs(draft.impact))}`
							: '—'}{' '}
					</p>
				</div>
			</div>
		</article>
	);
}

export default DraftScenarioCard;
