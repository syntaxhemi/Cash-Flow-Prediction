import type { OverviewMockData } from './types';

export const overviewMockData: OverviewMockData = {
	cashPosition: 184200,
	status: 'Above buffer',
	projectionDescription: 'Projected net cash flow for the next 30 days.',
	insight:
		'Liquidity remains comfortable, but receivables are slowing conversion.',
	forecastChart: {
		traces: [
			{
				path: 'M40 116 C90 108 108 125 150 112 S220 124 260 105 S330 115 370 92 S440 116 490 103 S530 112 555 106',
				color: 'var(--color-ink)',
			},
			{
				path: 'M555 106 C600 88 620 103 665 84 S735 94 775 76 S830 92 870 70 S920 78 960 58',
				color: 'var(--color-primary)',
			},
		],
		confidenceBand:
			'M555 78 C630 52 700 68 770 48 S880 62 960 34 L960 90 C870 108 800 92 730 112 S620 96 555 118Z',
		confidenceBandColor: 'var(--color-primary-soft)',
		today: { x: 555, y: 106 },
		yAxisLabels: [
			{ label: '₹400K', y: 65 },
			{ label: '₹200K', y: 83 },
			{ label: '₹0', y: 105 },
			{ label: '-₹200K', y: 128 },
			{ label: '-₹400K', y: 155 },
		],
		xAxisLabels: [
			{ label: 'Apr 15', x: 58 },
			{ label: 'Apr 22', x: 187 },
			{ label: 'Apr 29', x: 317 },
			{ label: 'May 6', x: 446 },
			{ label: 'May 13', x: 576 },
			{ label: 'May 20', x: 706 },
			{ label: 'May 27', x: 835 },
			{ label: 'Jun 3', x: 965 },
			{ label: 'Jun 10', x: 1094 },
			{ label: 'Jun 17', x: 1224 },
			{ label: 'Jun 24', x: 1382 },
		],
		mobileXAxisLabels: [
			{ label: 'Apr 15', x: 35 },
			{ label: 'May 6', x: 105 },
			{ label: 'May 13', x: 160 },
			{ label: 'May 27', x: 215 },
			{ label: 'Jun 10', x: 270 },
			{ label: 'Jun 24', x: 325 },
		],
		annotations: {
			aboveBuffer: ['Above buffer', 'through June'],
			buffer: 'Buffer',
		},
	},
	driver: {
		label: 'Main driver',
		title: 'Receivables are slowing conversion',
		corollary: '3 counterparties account for most of the modeled drag',
		linkLabel: 'Explore receivables',
		to: '/receivables',
	},
	recommendations: [
		{
			number: '01',
			title: 'Review Apex Retail receivable',
			detail: 'Highest modeled liquidity impact · Expected improvement ₹62K',
			action: 'Review receivable',
			to: '/receivables',
			featured: true,
		},
		{
			number: '02',
			title: 'Test payment-delay scenario',
			detail: 'Understand sensitivity to 15–30 day delays',
			action: 'Simulate',
			to: '/planning',
		},
		{
			number: '03',
			title: 'Check upcoming capex',
			detail: '₹1.2M planned over the next 45 days',
			action: 'Inspect',
			to: '/planning',
		},
	],
};
