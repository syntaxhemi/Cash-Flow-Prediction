export type ForecastPoint = { date: string; value: number };

export type ForecastSeries = {
	id: string;
	label: string;
	color: string;
	points: ForecastPoint[];
	strokeWidth?: number;
};

export type ForecastAxisLabel = { date: string; label: string };

export type ForecastChartData = {
	series: ForecastSeries[];
	uncertainty?: {
		upper: ForecastPoint[];
		lower: ForecastPoint[];
		color: string;
	};
	targetPeriod?: { start: string; end: string };
	forecastValue?: number;
	today: string;
	buffer: number;
	yAxisLabels: Array<{ label: string; value: number }>;
	xAxisLabels: ForecastAxisLabel[];
	annotations: {
		aboveBuffer: string[];
		buffer: string;
	};
};

export type ForecastImpact = {
	label: string;
	amount: string;
	detail: string;
	featured?: boolean;
};

export type ForecastRun = {
	label: string;
	time: string;
};

export type ForecastMockData = {
	chart: ForecastChartData;
	impacts: ForecastImpact[];
	runs: ForecastRun[];
	baselineSnapshot: string;
};
