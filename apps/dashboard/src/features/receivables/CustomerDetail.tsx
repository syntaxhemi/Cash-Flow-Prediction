import Button from '@/components/ui/Button';
import NumberInput from '@/components/ui/NumberInput';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/formatCurrency';
import type { Receivable } from './types';
import { priorityStyles } from './priorityStyles';

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

function formatCompactCurrency(value: number) {
	return formatCurrency(value, { maximumFractionDigits: 2 });
}

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

export default CustomerDetail;
