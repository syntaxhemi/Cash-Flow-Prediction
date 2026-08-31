import type {
	HealthScenario,
	HealthScenarioInput,
	HealthScenarioKey,
} from './types';

export const healthScenarioOptions: HealthScenario[] = [
	{ label: 'Credit score', value: 'credit_score' },
	{ label: 'Failure score', value: 'failure_score' },
	{ label: 'Debt-to-revenue ratio', value: 'debt_to_revenue_ratio' },
	{ label: 'Missed payments', value: 'missed_payments_number' },
];

export const healthScenarioInputs: Record<
	HealthScenarioKey,
	HealthScenarioInput
> = {
	credit_score: {
		label: 'Set to',
		min: 0,
		max: 1,
		defaultValue: 0.78,
		step: 0.01,
	},
	failure_score: {
		label: 'Set to',
		min: 0,
		max: 1,
		defaultValue: 0.18,
		step: 0.01,
	},
	debt_to_revenue_ratio: {
		label: 'Set to',
		min: 0,
		max: 1,
		defaultValue: 0.42,
		step: 0.01,
	},
	missed_payments_number: {
		label: 'Set to',
		unit: 'count',
		min: 0,
		max: 10,
		defaultValue: 1,
		step: 1,
	},
};

export const healthComparisonOptions: HealthScenario[] = [
	{ label: 'Baseline', value: 'baseline' },
];
