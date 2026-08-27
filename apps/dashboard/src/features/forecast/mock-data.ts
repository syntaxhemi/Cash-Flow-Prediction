import type { ForecastMockData } from './types';

const dates = [
	'2025-04-15',
	'2025-04-18',
	'2025-04-21',
	'2025-04-24',
	'2025-04-27',
	'2025-04-30',
	'2025-05-03',
	'2025-05-06',
	'2025-05-09',
	'2025-05-13',
	'2025-05-16',
	'2025-05-19',
	'2025-05-22',
	'2025-05-25',
	'2025-05-28',
	'2025-06-01',
	'2025-06-04',
	'2025-06-07',
	'2025-06-10',
	'2025-06-13',
	'2025-06-16',
	'2025-06-19',
	'2025-06-24',
] as const;

function points(values: number[]) {
	return dates.map((date, index) => ({ date, value: values[index] ?? 0 }));
}

export const forecastMockData: ForecastMockData = {
	chart: {
		series: [
			{
				id: 'recorded',
				label: 'Recorded',
				color: 'var(--color-ink)',
				points: points([
					-60000, -30000, -50000, -130000, -160000, -180000, -120000, -100000,
					-20000, 30000,
				]),
			},
			{
				id: 'baseline',
				label: 'Baseline',
				color: 'var(--color-primary)',
				points: points([
					30000, 50000, 40000, 60000, 50000, 80000, 65000, 100000, 85000, 90000,
					110000, 100000, 130000, 120000, 145000, 135000, 160000, 150000,
					175000, 165000, 185000, 175000, 195000,
				]),
			},
		],
		uncertainty: {
			upper: points([
				30000, 50000, 40000, 60000, 50000, 80000, 65000, 100000, 85000, 130000,
				180000, 170000, 210000, 190000, 230000, 210000, 250000, 230000, 270000,
				250000, 285000, 270000, 300000,
			]),
			lower: points([
				30000, 50000, 40000, 60000, 50000, 80000, 65000, 100000, 85000, 50000,
				30000, 20000, 40000, 30000, 60000, 40000, 80000, 60000, 100000, 80000,
				110000, 100000, 120000,
			]),
			color: 'var(--color-primary-soft)',
		},
		today: '2025-05-13',
		buffer: -200000,
		yAxisLabels: [
			{ label: '₹400K', value: 400000 },
			{ label: '₹200K', value: 200000 },
			{ label: '₹0', value: 0 },
			{ label: '-₹200K', value: -200000 },
			{ label: '-₹400K', value: -400000 },
		],
		xAxisLabels: [
			{ date: '2025-04-15', label: 'Apr 15' },
			{ date: '2025-04-29', label: 'Apr 29' },
			{ date: '2025-05-13', label: 'May 13' },
			{ date: '2025-05-27', label: 'May 27' },
			{ date: '2025-06-10', label: 'Jun 10' },
			{ date: '2025-06-24', label: 'Jun 24' },
		],
		annotations: {
			aboveBuffer: ['Above buffer', 'through June'],
			buffer: 'Buffer',
		},
	},
	impacts: [
		{
			label: 'Receivables',
			amount: '−₹62K',
			detail: 'Conversion slows by 4 days',
			featured: true,
		},
		{
			label: 'Operating costs',
			amount: '−₹18K',
			detail: 'Planned outflows remain stable',
		},
		{
			label: 'Collections',
			amount: '+₹44K',
			detail: 'Apex Retail timing improves',
		},
	],
	runs: [
		{ label: 'Latest run', time: '8 min ago' },
		{ label: 'Previous run', time: 'Yesterday' },
	],
	baselineSnapshot: 'Baseline snapshot',
};
