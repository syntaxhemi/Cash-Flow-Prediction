import type {
	ReceivablesListResponse,
	SimulationRun,
} from '@/api/contracts';
import { formatCurrency } from '@/utils/formatCurrency';
import type { Receivable, ReceivableRecord, ReceivablesSummary } from './types';

type ReceivableApiItem = NonNullable<ReceivablesListResponse['items']>[number];
type ReceivableApiRecord = NonNullable<ReceivableApiItem['records']>[number] & {
	amount_paid?: string | number | null;
	outstanding_amount?: string | number | null;
	payment_status?: string | null;
};

function numberValue(value: unknown) {
	if (typeof value !== 'string' && typeof value !== 'number') return null;
	const parsed = Number(value);
	return Number.isFinite(parsed) ? parsed : null;
}

function initials(name: string) {
	return name
		.split(/\s+/)
		.filter(Boolean)
		.slice(0, 2)
		.map((part) => part[0])
		.join('')
		.toUpperCase();
}

function formatDate(value: string | null | undefined) {
	if (!value) return 'No due date';
	return new Date(`${value}T00:00:00`).toLocaleDateString('en-IN', {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
	});
}

function dueLabel(records: ReceivableRecord[]) {
	const today = new Date();
	today.setHours(0, 0, 0, 0);
	const dueDates = records
		.map((record) => record.due)
		.filter(Boolean)
		.map((value) => new Date(`${value}T00:00:00`))
		.filter((value) => !Number.isNaN(value.getTime()));
	if (!dueDates.length) return 'No due-date records';
	const nearest = dueDates.reduce((earliest, value) =>
		value < earliest ? value : earliest,
	);
	const days = Math.round(
		(nearest.getTime() - today.getTime()) / (24 * 60 * 60 * 1000),
	);
	if (days < 0) return `${Math.abs(days)} days overdue`;
	if (days === 0) return 'Due today';
	return `Due in ${days} days`;
}

function recordStatus(status: string, paymentStatus?: string | null) {
	return paymentStatus === 'partially_paid'
		? 'Partially paid'
		: status === 'overdue'
		? 'Overdue'
		: status === 'pending'
			? 'Pending'
			: status === 'settled'
				? 'Settled'
				: 'Cancelled';
}

function recordView(
	record: ReceivableApiRecord,
): ReceivableRecord {
	return {
		id: record.id,
		invoice: record.reference_number ?? record.id.slice(0, 8).toUpperCase(),
		issued: formatDate(record.issued_date),
		due: formatDate(record.due_date),
		amount: Number(record.amount),
		amountPaid: numberValue(record.amount_paid) ?? 0,
		outstanding: numberValue(record.outstanding_amount) ?? Number(record.amount),
		status: recordStatus(record.status, record.payment_status),
	};
}

function counterpartyTypeLabel(value: string) {
	return value
		.split('_')
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(' ');
}

/** Adapts the Receivables read model and trapped-liquidity rankings for the UI. */
export function toReceivablesView(
	data: ReceivablesListResponse,
	simulation: SimulationRun | null,
): { items: Receivable[]; summary: ReceivablesSummary } {
	const rankings = simulation?.receivables_rankings ?? [];
	const items = (data.items ?? []).map((item) => {
		const ranking = rankings.find(
			(candidate) => candidate.counterparty_id === item.counterparty_id,
		);
		const records = (item.records ?? []).map(recordView);
		return {
			id: item.counterparty_id,
			name: item.name,
			shortName: initials(item.name),
			industry: counterpartyTypeLabel(item.counterparty_type),
			outstanding: Number(item.outstanding_amount),
			paidOnTime: numberValue(item.paid_on_time_percentage),
			medianDays: numberValue(item.average_payment_delay_days),
			lateInvoiceCount: item.late_invoice_count,
			dueLabel: dueLabel(records),
			predictedDelta: numberValue(ranking?.simulated_cashflow_delta) ?? 0,
			rank: ranking?.rank_position ?? null,
			records,
		};
	});
	const modeledTrappedLiquidity = items.reduce(
		(total, item) => total + Math.max(0, item.predictedDelta),
		0,
	);

	return {
		items,
		summary: {
			modeledTrappedLiquidity,
			totalOutstanding: Number(data.summary.total_outstanding),
			counterpartyCount: data.summary.counterparty_count,
			medianDays: numberValue(data.summary.median_payment_delay_days),
		},
	};
}

/** Formats a signed trapped-liquidity or payment-delay cash-flow delta. */
export function formatReceivableDelta(value: number) {
	const formatted = formatCurrency(Math.abs(value));
	return value < 0 ? `−${formatted}` : `+${formatted}`;
}
