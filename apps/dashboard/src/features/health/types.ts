export type HealthScenarioKey =
	| 'credit_score'
	| 'failure_score'
	| 'debt_to_revenue_ratio'
	| 'missed_payments_number';

export type HealthScenario = {
	label: string;
	value: HealthScenarioKey | 'baseline';
};

export type HealthScenarioInput = {
	label: string;
	unit?: string;
	min: number;
	max: number;
	defaultValue: number;
	step?: number;
};

export type HealthStat = {
	label: string;
	value: string;
	tone?: 'ink' | 'primary';
	supporting?: string;
};

export type HealthScore = {
	label: string;
	score: number;
	status: string;
	tone: 'primary' | 'soft';
};

export type HealthImpact = {
	label: string;
	amount: string;
	title: string;
	detail: string;
	tone: 'featured' | 'neutral' | 'soft';
};

export type HealthPageData = {
	stats: HealthStat[];
	scores: HealthScore[];
	healthDelta: string;
	healthDeltaValue: number;
	impacts: HealthImpact[];
};
