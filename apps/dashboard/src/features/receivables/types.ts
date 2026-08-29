export type ReceivablePriority = 'Critical' | 'High' | 'Watch' | 'Stable';

export type ReceivableRecord = {
	invoice: string;
	issued: string;
	due: string;
	amount: number;
	status: string;
};

export type Receivable = {
	id: string;
	name: string;
	shortName: string;
	industry: string;
	outstanding: number;
	paidOnTime: number;
	medianDays: number;
	dueLabel: string;
	predictedDelta: number;
	priority: ReceivablePriority;
	records: ReceivableRecord[];
};
