export type ForecastTrace = {
	path: string;
	color: string;
	strokeWidth?: number;
	fill?: string;
	opacity?: number;
};

export type ChartLabel = {
	label: string;
	x: number;
};

export type ForecastChartData = {
	traces: ForecastTrace[];
	confidenceBand: string;
	confidenceBandColor: string;
	today: { x: number; y: number };
	yAxisLabels: Array<{ label: string; y: number }>;
	xAxisLabels: ChartLabel[];
	mobileXAxisLabels: ChartLabel[];
	annotations: {
		aboveBuffer: string[];
		buffer: string;
	};
};

export type Recommendation = {
	number: string;
	title: string;
	detail: string;
	action: string;
	to: string;
	featured?: boolean;
};

export type OverviewMockData = {
	cashPosition: number;
	status: string;
	projectionDescription: string;
	insight: string;
	forecastChart: ForecastChartData;
	driver: {
		label: string;
		title: string;
		corollary: string;
		linkLabel: string;
		to: string;
	};
	recommendations: Recommendation[];
};
