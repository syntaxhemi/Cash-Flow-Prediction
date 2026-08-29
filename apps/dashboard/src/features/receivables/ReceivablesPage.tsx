import { useMemo, useState } from 'react';
import Button from '@/components/ui/Button';
import Dropdown, { type DropdownOption } from '@/components/ui/Dropdown';
import NumberInput from '@/components/ui/NumberInput';
import SegmentedControl from '@/components/ui/SegmentedControl';
import PageLayout from '@/components/layout/PageLayout';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/formatCurrency';
import { receivablesMockData, receivablesSummary } from './mock-data';
import type { Receivable, ReceivablePriority } from './types';

const horizonOptions = [
	{ label: '30 days', value: '30' },
	{ label: '60 days', value: '60' },
	{ label: '90 days', value: '90' },
] as const;

const sortOptions: DropdownOption[] = [
	{ label: 'Cash impact', value: 'impact' },
	{ label: 'Outstanding amount', value: 'amount' },
	{ label: 'Payment delay', value: 'delay' },
];

const accountOptions: DropdownOption[] = [
	{ label: 'All open receivables', value: 'all' },
	{ label: 'Overdue only', value: 'overdue' },
	{ label: 'Due in 30 days', value: 'upcoming' },
];

const priorityStyles: Record<ReceivablePriority, string> = {
	Critical: 'bg-primary-soft text-primary',
	High: 'bg-[#f7eee6] text-warning',
	Watch: 'bg-canvas text-ink',
	Stable: 'bg-[#e9f0eb] text-positive',
};

function ArrowUpRight() {
	return (
		<svg viewBox="0 0 16 16" className="size-4" aria-hidden="true">
			<path
				d="M4 12 12 4M5 4h7v7"
				fill="none"
				stroke="currentColor"
				strokeLinecap="round"
				strokeLinejoin="round"
				strokeWidth="1.4"
			/>
		</svg>
	);
}

function ChevronRight({ className }: { className?: string }) {
	return (
		<svg
			viewBox="0 0 16 16"
			className={cn('size-4 transition-transform', className)}
			aria-hidden="true"
		>
			<path
				d="m6 3 5 5-5 5"
				fill="none"
				stroke="currentColor"
				strokeLinecap="round"
				strokeLinejoin="round"
				strokeWidth="1.4"
			/>
		</svg>
	);
}

function formatCompactCurrency(value: number) {
	return formatCurrency(value, { maximumFractionDigits: 2 });
}

type CustomerDetailProps = {
	receivable: Receivable;
	delayDays: number;
	onDelayChange: (value: number) => void;
	simulationRun: boolean;
	onPreview: () => void;
	id: string;
	titleId: string;
	className?: string;
};

function CustomerDetail({
	receivable,
	delayDays,
	onDelayChange,
	simulationRun,
	onPreview,
	id,
	titleId,
	className,
}: CustomerDetailProps) {
	const simulatedDelta = Math.round(
		(Math.abs(receivable.predictedDelta) * Math.min(delayDays, 14)) / 14,
	);

	return (
		<aside
			id={id}
			className={cn(
				'rounded-card border border-border bg-surface p-6 sm:p-7',
				className,
			)}
			aria-labelledby={titleId}
		>
			<div className="flex items-start justify-between gap-4">
				<div className="flex items-center gap-3">
					<div className="grid size-10 place-items-center rounded-full bg-primary-soft text-xs font-semibold text-primary">
						{receivable.shortName}
					</div>
					<div>
						<p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-text-muted">
							Selected customer
						</p>
						<h3 id={titleId} className="mt-1 text-lg font-medium text-ink">
							{receivable.name}
						</h3>
					</div>
				</div>
				<span
					className={cn(
						'rounded-full px-2.5 py-1 text-[11px] font-medium',
						priorityStyles[receivable.priority],
					)}
				>
					{receivable.priority}
				</span>
			</div>
			<p className="mt-4 text-sm text-text-muted">{receivable.industry}</p>

			<div className="mt-6 grid grid-cols-2 gap-x-6 gap-y-5 rounded-control bg-canvas/70 p-4">
				<div>
					<p className="text-xs text-text-muted">Outstanding</p>
					<p className="mt-1 text-lg tabular-nums text-ink lg:text-xl">
						{formatCompactCurrency(receivable.outstanding)}
					</p>
				</div>
				<div>
					<p className="text-xs text-text-muted">Cash impact</p>
					<p className="mt-1 text-lg tabular-nums text-primary lg:text-xl">
						−{formatCompactCurrency(Math.abs(receivable.predictedDelta))}
					</p>
				</div>
				<div>
					<p className="text-xs text-text-muted">Paid on time</p>
					<p className="mt-1 text-sm tabular-nums text-ink lg:text-base">
						{receivable.paidOnTime}%
					</p>
				</div>
				<div>
					<p className="text-xs text-text-muted">Typical payment</p>
					<p className="mt-1 text-sm tabular-nums text-ink lg:text-base">
						{receivable.medianDays} days
					</p>
				</div>
			</div>

			<div className="mt-4 pt-1">
				<p className="text-xs font-semibold uppercase tracking-widest text-simulation">
					Test a payment delay
				</p>
				<p className="mt-2 text-sm leading-relaxed text-text-muted">
					See how a later payment could change the baseline cash position.
				</p>
				<div className="mt-4 flex flex-nowrap items-end justify-between gap-3">
					<NumberInput
						label="Delay by"
						value={delayDays}
						unit="days"
						min={1}
						max={14}
						onChange={onDelayChange}
					/>
					<Button
						variant="soft"
						size="sm"
						onClick={onPreview}
						className="shrink-0"
					>
						Preview impact
					</Button>
				</div>
				{simulationRun && (
					<div className="mt-5 rounded-control bg-[#f2edf1] p-4" role="status">
						<div className="flex items-center justify-between gap-4">
							<span className="text-xs text-text-muted">
								Estimated cash impact
							</span>
							<span className="text-sm font-medium tabular-nums text-simulation">
								−{formatCompactCurrency(simulatedDelta)}
							</span>
						</div>
						<p className="mt-2 text-xs leading-relaxed text-text-muted">
							If {receivable.name} pays {delayDays} days later, this is the
							estimated additional pressure on the selected outlook.
						</p>
					</div>
				)}
			</div>
		</aside>
	);
}

/** Renders the static receivables impact and payment-delay decision surface. */
function ReceivablesPage() {
	const [selectedId, setSelectedId] = useState(receivablesMockData[0].id);
	const [horizon, setHorizon] =
		useState<(typeof horizonOptions)[number]['value']>('30');
	const [sortBy, setSortBy] = useState('impact');
	const [accountFilter, setAccountFilter] = useState('all');
	const [delayDays, setDelayDays] = useState(4);
	const [simulationRun, setSimulationRun] = useState(false);

	const selectedReceivable =
		receivablesMockData.find((receivable) => receivable.id === selectedId) ??
		receivablesMockData[0];

	const sortedReceivables = useMemo(() => {
		const filtered = receivablesMockData.filter((receivable) => {
			if (accountFilter === 'overdue')
				return receivable.dueLabel.includes('overdue');
			if (accountFilter === 'upcoming')
				return !receivable.dueLabel.includes('overdue');
			return true;
		});

		return [...filtered].sort((left, right) => {
			if (sortBy === 'amount') return right.outstanding - left.outstanding;
			if (sortBy === 'delay') return right.medianDays - left.medianDays;
			return Math.abs(right.predictedDelta) - Math.abs(left.predictedDelta);
		});
	}, [accountFilter, sortBy]);

	const maximumImpact = Math.max(
		...receivablesMockData.map((receivable) =>
			Math.abs(receivable.predictedDelta),
		),
	);
	const visibleRecords = selectedReceivable.records;
	function selectReceivable(id: string) {
		setSelectedId(id);
		setSimulationRun(false);
	}

	return (
		<PageLayout title="Receivables">
			<header className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
				<div>
					<p className="text-xs font-semibold uppercase tracking-widest text-primary">
						Receivables &amp; trapped liquidity
					</p>
					<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
						Receivables
					</h1>
					<p className="mt-4 max-w-2xl text-base text-text-muted sm:text-lg">
						Prioritize the customers whose payment timing could change your
						near-term cash outlook.
					</p>
				</div>
			</header>

			<section
				className="mt-10 flex flex-col gap-4 py-2 lg:flex-row lg:items-center lg:justify-between"
				aria-label="Receivables controls"
			>
				<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
					<span className="text-sm font-medium text-ink">View window</span>
					<SegmentedControl
						options={horizonOptions}
						value={horizon}
						onChange={setHorizon}
						size="sm"
					/>
				</div>
				<div className="grid grid-cols-2 gap-3 sm:flex sm:items-center sm:gap-3">
					<Dropdown
						label="Account filter"
						options={accountOptions}
						value={accountFilter}
						onChange={setAccountFilter}
						className="w-full shrink-0 sm:w-56"
						size="sm"
					/>
					<Dropdown
						label="Sort receivables"
						options={sortOptions}
						value={sortBy}
						onChange={setSortBy}
						className="w-full shrink-0 sm:w-48"
						size="sm"
					/>
					<Button
						size="sm"
						leading={<ArrowUpRight />}
						className="col-span-2 w-full sm:col-span-1 sm:w-auto"
					>
						Run analysis
					</Button>
				</div>
			</section>

			<section
				className="mt-14 grid gap-12 lg:grid-cols-[minmax(0,1.25fr)_minmax(20rem,0.75fr)] lg:items-start lg:gap-20"
				aria-label="Receivables summary"
			>
				<article className="rounded-card bg-primary-soft p-6 sm:p-8">
					<p className="text-xs font-semibold uppercase tracking-widest text-primary">
						Cash tied up in late payments
					</p>
					<div className="mt-4 flex flex-wrap items-baseline gap-x-4 gap-y-2">
						<p className="text-4xl font-medium tracking-tight text-primary sm:text-5xl">
							{formatCompactCurrency(
								receivablesSummary.modeledTrappedLiquidity,
							)}
						</p>
						<span className="text-sm text-text-muted">
							across {receivablesSummary.counterpartyCount} customers
						</span>
					</div>
					<p className="mt-4 max-w-xl text-sm leading-relaxed text-ink sm:text-base">
						Estimated cash that could return to the forecast if the
						highest-impact customers paid on schedule.
					</p>
					<div className="mt-8 grid max-w-xl grid-cols-2 gap-6 pt-1">
						<div>
							<p className="text-xs text-text-muted">Open balance</p>
							<p className="mt-1 text-xl tabular-nums text-ink">
								{formatCompactCurrency(receivablesSummary.totalOutstanding)}
							</p>
						</div>
						<div>
							<p className="text-xs text-text-muted">Median payment</p>
							<p className="mt-1 text-xl tabular-nums text-ink">
								{receivablesSummary.medianDays} days
							</p>
						</div>
					</div>
				</article>

				<div className="pt-1 lg:pt-6">
					<p className="text-xs font-semibold uppercase tracking-widest text-primary">
						Collection opportunity
					</p>
					<h2 className="mt-4 max-w-md font-serif text-2xl leading-tight text-ink sm:text-3xl">
						Apex Retail is the clearest near-term collection opportunity.
					</h2>
					<p className="mt-3 max-w-md text-sm leading-relaxed text-text-muted sm:text-base">
						Its outstanding balance has the greatest expected effect on
						near-term cash, and it typically pays 7 days later than the
						portfolio median.
					</p>
					<a
						href="#customer-detail-desktop"
						className="mt-5 hidden items-center gap-2 text-sm font-medium text-primary no-underline hover:underline lg:inline-flex"
					>
						Inspect the priority customer <ArrowUpRight />
					</a>
					<a
						href="#customer-detail-mobile"
						className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline lg:hidden"
					>
						Inspect the priority customer <ArrowUpRight />
					</a>
				</div>
			</section>

			<section
				className="mt-16 sm:mt-20"
				aria-labelledby="impact-ranking-title"
			>
				<div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
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
				</div>

				<div className="mt-8 grid gap-10 lg:grid-cols-[minmax(0,1.45fr)_minmax(22rem,0.85fr)] lg:gap-12 xl:gap-20">
					<div>
						<div className="hidden grid-cols-[2rem_minmax(16rem,1fr)_10rem_9rem_6rem] gap-4 px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-text-muted sm:grid">
							<span>#</span>
							<span>Customer</span>
							<span>Outstanding</span>
							<span>Cash impact</span>
							<span>Priority</span>
						</div>
						<ol className="space-y-1">
							{sortedReceivables.map((receivable, index) => {
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
											onClick={() => selectReceivable(receivable.id)}
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
													<ChevronRight
														className={cn(
															isSelected && 'rotate-90 lg:rotate-0',
														)}
													/>
												</span>
												<span className="mt-1 block text-xs text-text-muted">
													{receivable.dueLabel} · typical payment time{' '}
													{receivable.medianDays} days
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
												{formatCompactCurrency(receivable.outstanding)}
											</span>
											<span className="whitespace-nowrap text-left text-sm font-medium tabular-nums text-primary">
												−
												{formatCompactCurrency(
													Math.abs(receivable.predictedDelta),
												)}
											</span>
											<span
												className={cn(
													'hidden w-fit justify-self-start rounded-full px-2.5 py-1 text-[11px] font-medium sm:inline-flex',
													priorityStyles[receivable.priority],
												)}
											>
												{receivable.priority}
											</span>
										</button>
										{isSelected && (
											<CustomerDetail
												receivable={selectedReceivable}
												delayDays={delayDays}
												onDelayChange={setDelayDays}
												simulationRun={simulationRun}
												onPreview={() => setSimulationRun(true)}
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
							Showing {sortedReceivables.length} of{' '}
							{receivablesSummary.counterpartyCount} open customers · {horizon}
							-day outlook
						</p>
					</div>

					<CustomerDetail
						receivable={selectedReceivable}
						delayDays={delayDays}
						onDelayChange={setDelayDays}
						simulationRun={simulationRun}
						onPreview={() => setSimulationRun(true)}
						id="customer-detail-desktop"
						titleId="customer-detail-desktop-title"
						className="hidden lg:block"
					/>
				</div>
			</section>

			<section
				className="mt-20 pt-1 sm:mt-24"
				aria-labelledby="supporting-records-title"
			>
				<div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
					<div>
						<p className="text-xs font-semibold uppercase tracking-widest text-text-muted">
							Supporting records
						</p>
						<h2
							id="supporting-records-title"
							className="mt-2 font-serif text-2xl leading-tight text-ink"
						>
							Invoices behind the selected balance
						</h2>
					</div>
					<p className="text-sm text-text-muted">
						{selectedReceivable.name} · {selectedReceivable.records.length}{' '}
						records
					</p>
				</div>
				<div className="mt-6 overflow-hidden rounded-card border border-border bg-surface">
					<div className="hidden grid-cols-[8rem_minmax(14rem,1fr)_10rem_10rem_10rem] gap-4 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-text-muted sm:grid">
						<span>Invoice</span>
						<span>Issued</span>
						<span>Due</span>
						<span>Amount</span>
						<span>Status</span>
					</div>
					<div className="space-y-1 p-1">
						{visibleRecords.map((record) => (
							<div
								key={record.invoice}
								className="grid gap-2 rounded-control px-4 py-4 hover:bg-primary-soft/40 sm:grid-cols-[8rem_minmax(14rem,1fr)_10rem_10rem_10rem] sm:items-center sm:gap-4"
							>
								<div>
									<p className="text-sm font-medium text-ink">
										{record.invoice}
									</p>
									<p className="mt-1 text-xs text-text-muted sm:hidden">
										Issued {record.issued} · Due {record.due}
									</p>
								</div>
								<span className="hidden text-sm text-text-muted sm:block">
									{record.issued}
								</span>
								<span className="hidden text-sm text-text-muted sm:block">
									{record.due}
								</span>
								<span className="text-sm tabular-nums text-ink">
									{formatCompactCurrency(record.amount)}
								</span>
								<span
									className={cn(
										'w-fit rounded-full px-2.5 py-1 text-[11px] font-medium',
										record.status === 'Overdue'
											? 'bg-primary-soft text-primary'
											: record.status === 'Due soon'
												? 'bg-[#f7eee6] text-warning'
												: 'bg-[#e9f0eb] text-positive',
									)}
								>
									{record.status}
								</span>
							</div>
						))}
					</div>
				</div>
			</section>

			<p className="mt-10 text-xs leading-relaxed text-text-muted">
				Estimates on this page show how payment timing could affect the baseline
				forecast. They are decision support, not a confirmed collection outcome.
			</p>
		</PageLayout>
	);
}

export default ReceivablesPage;
