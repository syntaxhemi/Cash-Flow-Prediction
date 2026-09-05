export type ReceivableRecord = {
	id: string;
	invoice: string;
	issued: string;
	due: string;
	amount: number;
	amountPaid: number;
	outstanding: number;
	status: string;
};

export type Receivable = {
	id: string;
	name: string;
	shortName: string;
	industry: string;
	outstanding: number;
	paidOnTime: number | null;
	medianDays: number | null;
	lateInvoiceCount: number;
	dueLabel: string;
	predictedDelta: number;
	rank: number | null;
	records: ReceivableRecord[];
};

export type ReceivablesSummary = {
	modeledTrappedLiquidity: number;
	totalOutstanding: number;
	counterpartyCount: number;
	medianDays: number | null;
};
