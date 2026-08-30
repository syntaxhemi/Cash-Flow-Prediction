import { useMemo, useState } from 'react';
import { LuArrowUpRight } from 'react-icons/lu';
import PageLayout from '@/components/layout/PageLayout';
import { formatCurrency } from '@/utils/formatCurrency';
import ImpactRanking from './ImpactRanking';
import {
	horizonOptions,
	receivablesMockData,
	receivablesSummary,
} from './mock-data';
import ReceivablesControls from './ReceivablesControls';
import SupportingRecords from './SupportingRecords';

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

	function selectReceivable(id: string) {
		setSelectedId(id);
		setSimulationRun(false);
	}

	return (
		<PageLayout title="Receivables">
			<header>
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
			</header>

			<ReceivablesControls
				horizon={horizon}
				onHorizonChange={setHorizon}
				sortBy={sortBy}
				onSortChange={setSortBy}
				accountFilter={accountFilter}
				onAccountFilterChange={setAccountFilter}
			/>

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
							{formatCurrency(receivablesSummary.modeledTrappedLiquidity)}
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
								{formatCurrency(receivablesSummary.totalOutstanding)}
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
						Inspect the priority customer <LuArrowUpRight className="size-4" />
					</a>
					<a
						href="#customer-detail-mobile"
						className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline lg:hidden"
					>
						Inspect the priority customer <LuArrowUpRight className="size-4" />
					</a>
				</div>
			</section>

			<ImpactRanking
				receivables={sortedReceivables}
				selectedReceivable={selectedReceivable}
				maximumImpact={maximumImpact}
				onSelect={selectReceivable}
				delayDays={delayDays}
				onDelayChange={setDelayDays}
				simulationRun={simulationRun}
				onPreview={() => setSimulationRun(true)}
				visibleCount={sortedReceivables.length}
				counterpartyCount={receivablesSummary.counterpartyCount}
				horizon={horizon}
			/>
			<SupportingRecords receivable={selectedReceivable} />
			<p className="mt-10 text-xs leading-relaxed text-text-muted">
				Estimates on this page show how payment timing could affect the baseline
				forecast. They are decision support, not a confirmed collection outcome.
			</p>
		</PageLayout>
	);
}

export default ReceivablesPage;
