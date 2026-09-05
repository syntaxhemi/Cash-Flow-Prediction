import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/formatCurrency';
import type { Receivable } from './types';

type SupportingRecordsProps = { receivable: Receivable };

function SupportingRecords({ receivable }: SupportingRecordsProps) {
	return (
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
					{receivable.name} · {receivable.records.length} records
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
					{receivable.records.map((record) => (
						<div
							key={record.invoice}
							className="grid gap-2 rounded-control px-4 py-4 hover:bg-primary-soft/40 sm:grid-cols-[8rem_minmax(14rem,1fr)_10rem_10rem_10rem] sm:items-center sm:gap-4"
						>
							<div>
								<p className="text-sm font-medium text-ink">{record.invoice}</p>
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
								<div>{formatCurrency(record.outstanding)}</div>
								{record.amountPaid > 0 && (
									<div className="mt-1 text-xs text-text-muted">
										{formatCurrency(record.amountPaid)} paid of{' '}
										{formatCurrency(record.amount)}
									</div>
								)}
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
	);
}

export default SupportingRecords;
