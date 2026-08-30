import type { ForecastRun as ApiForecastRun } from '@/api/contracts';
import { formatCurrency } from '@/utils/formatCurrency';
import type { ForecastChartData, ForecastImpact, ForecastRun } from './types';

export type ForecastView = {
	chart: ForecastChartData;
	impacts: ForecastImpact[];
	runs: ForecastRun[];
	baselineSnapshot: string;
	readout: { heading: string; description: string };
	cashMovement: {
		inflows: string;
		outflows: string;
		inflowsValue: number;
		outflowsValue: number;
		detail: string;
	};
};

function dateLabel(value: string) {
	return new Date(`${value}T00:00:00`).toLocaleDateString('en-IN', {
		day: 'numeric',
		month: 'short',
	});
}

function formatMoney(value: number) {
	return formatCurrency(Math.abs(value));
}

function axisLabelsFor(values: number[]) {
	const minimum = Math.min(...values, 0);
	const maximum = Math.max(...values, 0);
	const padding = Math.max((maximum - minimum) * 0.1, 1);
	const lowerBound = minimum - padding;
	const upperBound = maximum + padding;

	return Array.from({ length: 5 }, (_, index) => {
		const value = upperBound - ((upperBound - lowerBound) / 4) * index;
		return { label: formatCurrency(value), value };
	});
}

function formatRunTime(value: string) {
	return new Date(value).toLocaleString('en-IN', {
		day: 'numeric',
		month: 'short',
		hour: 'numeric',
		minute: '2-digit',
	});
}

function chartFor(run: ApiForecastRun): ForecastChartData {
	const periods = [...(run.periods ?? [])].sort(
		(left, right) => left.sequence_index - right.sequence_index,
	);
	const recorded = periods.map((period) => ({
		date: period.period_end,
		value: Number(period.net_cashflow),
	}));
	const baseline = [
		...(recorded.length > 0 ? [recorded[recorded.length - 1]] : []),
		{
			date: run.target_period_start,
			value: Number(run.predicted_net_cashflow),
		},
		{ date: run.target_period_end, value: Number(run.predicted_net_cashflow) },
	];
	const forecastValue = Number(run.predicted_net_cashflow);
	const buffer = Number(run.solvency_buffer);
	const allDates = [
		...new Set([...recorded, ...baseline].map((point) => point.date)),
	].sort();
	const labelDates = allDates.filter(
		(_, index) =>
			index === 0 ||
			index === allDates.length - 1 ||
			index === Math.floor((allDates.length - 1) / 2),
	);

	return {
		series: [
			{
				id: 'recorded',
				label: 'Recorded',
				color: 'var(--color-ink)',
				points: recorded,
			},
			{
				id: 'baseline',
				label: 'Baseline',
				color: 'var(--color-primary)',
				points: baseline,
			},
		],
		targetPeriod: {
			start: run.target_period_start,
			end: run.target_period_end,
		},
		forecastValue,
		today: run.target_period_start,
		buffer,
		yAxisLabels: axisLabelsFor([
			...recorded.map((point) => point.value),
			forecastValue,
			buffer,
		]),
		xAxisLabels: labelDates.map((date) => ({ date, label: dateLabel(date) })),
		annotations: {
			aboveBuffer: ['Forecast period'],
			buffer: 'Buffer',
		},
	};
}

function impactsFor(run: ApiForecastRun) {
	return (run.observation_drivers ?? []).map((driver, index) => ({
		label: driver.label,
		amount: formatMoney(Number(driver.value)),
		detail: driver.detail,
		featured: index === 0,
	}));
}

function runsFor(runs: ApiForecastRun[]) {
	return runs.slice(0, 2).map((run, index) => ({
		label: index === 0 ? 'Latest run' : 'Previous run',
		time: formatRunTime(run.requested_at),
	}));
}

/** Adapt the forecast API read model to the existing Forecast page design. */
export function toForecastView(
	run: ApiForecastRun,
	allRuns: ApiForecastRun[] = [run],
): ForecastView {
	const aboveBuffer = Number(run.buffer_gap) >= 0;
	return {
		chart: chartFor(run),
		impacts: impactsFor(run),
		runs: runsFor(allRuns),
		baselineSnapshot: 'Baseline snapshot',
		readout: {
			heading: aboveBuffer
				? 'The baseline stays clear of the buffer.'
				: 'The baseline falls below the buffer.',
			description:
				run.observations?.[1] ??
				'Projected net cash flow is compared with the configured solvency buffer.',
		},
		cashMovement: {
			inflowsValue: Number(run.expected_inflows),
			outflowsValue: Number(run.expected_outflows),
			inflows: formatMoney(Number(run.expected_inflows)),
			outflows: formatMoney(Number(run.expected_outflows)),
			detail: 'Expected cash movements within the selected period.',
		},
	};
}
