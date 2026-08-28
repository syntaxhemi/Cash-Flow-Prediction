import type {
	HealthPageData,
	HealthScenario,
	HealthScenarioInput,
	HealthScenarioKey,
} from './types';

export const healthScenarioOptions: HealthScenario[] = [
	{ label: 'Delayed collections', value: 'delayed-collections' },
	{ label: 'Operating costs', value: 'operating-costs' },
	{ label: 'Cash buffer', value: 'cash-buffer' },
];

export const healthScenarioInputs: Record<
	HealthScenarioKey,
	HealthScenarioInput
> = {
	'delayed-collections': {
		label: 'Delay by',
		unit: 'days',
		min: 1,
		max: 90,
		defaultValue: 4,
	},
	'operating-costs': {
		label: 'Increase by',
		unit: 'percent',
		min: 1,
		max: 100,
		defaultValue: 5,
	},
	'cash-buffer': {
		label: 'Change by',
		unit: 'percent',
		min: 1,
		max: 100,
		defaultValue: 10,
	},
};

export const healthComparisonOptions: HealthScenario[] = [
	{ label: 'Baseline', value: 'baseline' },
];

export const healthMockData: HealthPageData = {
	stats: [
		{
			label: 'Cash delta',
			value: '−₹62K',
			tone: 'primary',
			supporting: 'Delayed collections · +4 days',
		},
		{ label: 'Baseline cash', value: '₹1.58M' },
		{ label: 'Simulated cash', value: '₹1.52M', tone: 'primary' },
		{
			label: 'Above buffer',
			value: '₹0.62M',
			tone: 'primary',
		},
	],
	scores: [
		{
			label: 'Baseline',
			score: 78,
			status: 'Comfortable',
			tone: 'primary',
		},
		{
			label: 'Delayed collections',
			score: 64,
			status: 'At risk',
			tone: 'soft',
		},
	],
	healthDelta: '−14 health points',
	impacts: [
		{
			label: 'Receivables',
			amount: '−10 points',
			title: 'Receivables conversion',
			detail: '41 days · 5 days behind plan',
			tone: 'featured',
		},
		{
			label: 'Operating costs',
			amount: '−5 points',
			title: 'Run-rate',
			detail: '₹6.35M / mo · +5% vs plan',
			tone: 'neutral',
		},
		{
			label: 'Cash buffer',
			amount: '+1 point',
			title: 'Cash buffer',
			detail: '₹0.90M · +10% vs plan',
			tone: 'soft',
		},
	],
};
