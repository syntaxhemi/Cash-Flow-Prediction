import { LuChevronRight } from 'react-icons/lu';
import type { SimulationRun } from '@/api/contracts';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/formatCurrency';
import CustomerDetail from './CustomerDetail';
import { formatReceivableDelta } from './adapters';
import type { Receivable } from './types';

type ImpactRankingProps = {
	receivables: Receivable[];
	selectedReceivable: Receivable;
	maximumImpact: number;
	onSelect: (id: string) => void;
	delayDays: number;
	onDelayChange: (value: number) => void;
	simulationRun: boolean;
	onPreview: () => void;
	previewPending: boolean;
	previewSimulation: SimulationRun | null;
	visibleCount: number;
	counterpartyCount: number;
	horizon: string;
};

function ImpactRanking({
	receivables,
	selectedReceivable,
	maximumImpact,
	onSelect,
	delayDays,
	onDelayChange,
	simulationRun,
	onPreview,
	previewPending,
	previewSimulation,
	visibleCount,
	counterpartyCount,
	horizon,
}: ImpactRankingProps) {
	return (
		<section className="mt-16 sm:mt-20" aria-labelledby="impact-ranking-title">
			<div>
				<p className="text-xs font-semibold uppercase tracking-widest text-text-muted">
					Cash impact ranking
				</p>
				<h2
					id="impact-ranking-title"
					className="mt-2 font-serif text-2xl leading-tight text-ink sm:text-3xl"
				>
					Where cash is waiting
				</h2>
			</div>
			<div className="mt-8 grid gap-10 lg:grid-cols-[minmax(0,1.45fr)_minmax(22rem,0.85fr)] lg:gap-12 xl:gap-20">
				<div>
					<div className="hidden grid-cols-[2rem_minmax(16rem,1fr)_10rem_9rem_6rem] gap-4 px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-text-muted sm:grid">
						<span>#</span>
						<span>Customer</span>
						<span>Outstanding</span>
						<span>Cash impact</span>
						<span>Rank</span>
					</div>
					<ol className="space-y-1">
						{receivables.map((receivable, index) => {
							const isSelected = selectedReceivable.id === receivable.id;
							const impactWidth = `${Math.max(13, (Math.abs(receivable.predictedDelta) / maximumImpact) * 100)}%`;
							return (
								<li key={receivable.id}>
									<button
										type="button"
										className={cn(
											'group grid w-full grid-cols-[2rem_minmax(0,1fr)_auto] items-center gap-3 rounded-control px-3 py-4 text-left transition sm:grid-cols-[2rem_minmax(16rem,1fr)_10rem_9rem_6rem] sm:gap-4',
											isSelected
												? 'bg-surface shadow-[0_0_0_1px_var(--color-border)]'
												: 'hover:bg-primary-soft/50',
										)}
										onClick={() => onSelect(receivable.id)}
										aria-pressed={isSelected}
									>
										<span className="self-start pt-1 text-xs tabular-nums text-text-muted">
											{String(index + 1).padStart(2, '0')}
										</span>
										<span className="min-w-0">
											<span className="flex items-center gap-2">
												<span className="truncate text-sm font-medium text-ink">
													{receivable.name}
												</span>
												<LuChevronRight
													className={cn(
														'size-4 transition-transform',
														isSelected && 'rotate-90 lg:rotate-0',
													)}
													aria-hidden="true"
												/>
											</span>
											<span className="mt-1 block text-xs text-text-muted">
								{receivable.dueLabel} · typical payment time{' '}
								{receivable.medianDays === null
									? '—'
									: `${receivable.medianDays} days`}
											</span>
											<span
												className="mt-3 block h-1.5 w-full max-w-xs rounded-full bg-border/70"
												aria-hidden="true"
											>
												<span
													className="block h-full rounded-full bg-primary"
													style={{ width: impactWidth }}
												/>
											</span>
										</span>
										<span className="hidden whitespace-nowrap text-left text-sm tabular-nums text-ink sm:block">
											{formatCurrency(receivable.outstanding)}
										</span>
						<span className="whitespace-nowrap text-left text-sm font-medium tabular-nums text-primary">
							{formatReceivableDelta(receivable.predictedDelta)}
										</span>
						<span className="hidden w-fit justify-self-start text-sm tabular-nums text-text-muted sm:inline-flex">
							{receivable.rank === null ? '—' : `#${receivable.rank}`}
						</span>
									</button>
									{isSelected && (
										<CustomerDetail
											receivable={selectedReceivable}
											delayDays={delayDays}
											onDelayChange={onDelayChange}
										simulationRun={simulationRun}
										onPreview={onPreview}
										previewPending={previewPending}
										previewSimulation={previewSimulation}
											id="customer-detail-mobile"
											titleId="customer-detail-mobile-title"
											className="mt-4 lg:hidden"
										/>
									)}
								</li>
							);
						})}
					</ol>
					<p className="mt-4 px-3 text-xs text-text-muted">
						Showing {visibleCount} of {counterpartyCount} open customers ·{' '}
						{horizon}-day outlook
					</p>
				</div>
				<CustomerDetail
					receivable={selectedReceivable}
					delayDays={delayDays}
					onDelayChange={onDelayChange}
					simulationRun={simulationRun}
					onPreview={onPreview}
					previewPending={previewPending}
					previewSimulation={previewSimulation}
					id="customer-detail-desktop"
					titleId="customer-detail-desktop-title"
					className="hidden lg:block"
				/>
			</div>
		</section>
	);
}

export default ImpactRanking;
