export type HealthScenarioKey =
	'delayed-collections' | 'operating-costs' | 'cash-buffer';

export type HealthScenario = {
	label: string;
	value: HealthScenarioKey | 'baseline';
};

export type HealthScenarioInput = {
	label: string;
	unit: 'days' | 'percent';
	min: number;
	max: number;
	defaultValue: number;
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
	impacts: HealthImpact[];
};
