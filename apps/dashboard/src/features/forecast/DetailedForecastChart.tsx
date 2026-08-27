import type { ForecastChartData, ForecastPoint } from './types';

type Plot = { left: number; right: number; top: number; bottom: number };

function xFor(date: string, dates: string[], plot: Plot) {
	const firstDate = Date.parse(dates[0] ?? date);
	const lastDate = Date.parse(dates.at(-1) ?? date);
	const range = Math.max(lastDate - firstDate, 1);
	const position = Math.min(Math.max(Date.parse(date) - firstDate, 0), range);
	return plot.left + (position / range) * (plot.right - plot.left);
}

function yFor(value: number, plot: Plot) {
	return plot.top + ((400000 - value) / 800000) * (plot.bottom - plot.top);
}

function pathFor(points: ForecastPoint[], dates: string[], plot: Plot) {
	return points
		.map(
			(point, index) =>
				`${index ? 'L' : 'M'} ${xFor(point.date, dates, plot)} ${yFor(point.value, plot)}`,
		)
		.join(' ');
}

function bandFor(
	upper: ForecastPoint[],
	lower: ForecastPoint[],
	dates: string[],
	plot: Plot,
) {
	return `${pathFor(upper, dates, plot)} ${lower
		.slice()
		.reverse()
		.map(
			(point) =>
				`L ${xFor(point.date, dates, plot)} ${yFor(point.value, plot)}`,
		)
		.join(' ')} Z`;
}

function ChartSvg({
	data,
	mobile = false,
}: {
	data: ForecastChartData;
	mobile?: boolean;
}) {
	const width = mobile ? 360 : 1000;
	const height = mobile ? 300 : 360;
	const plot = mobile
		? { left: 52, right: 346, top: 38, bottom: 238 }
		: { left: 72, right: 972, top: 42, bottom: 292 };
	const dates = data.series[0]?.points.map((point) => point.date) ?? [];
	const todayX = xFor(data.today, dates, plot);
	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			className="h-auto w-full"
			role="img"
			aria-label="Detailed baseline cash flow forecast"
		>
			{data.yAxisLabels.map((label) => {
				const y = yFor(label.value, plot);
				return (
					<line
						key={label.value}
						x1={plot.left}
						x2={plot.right}
						y1={y}
						y2={y}
						stroke={
							label.value === data.buffer
								? 'var(--color-ink)'
								: 'var(--color-border)'
						}
						strokeDasharray={label.value === data.buffer ? '5 6' : undefined}
					/>
				);
			})}
			<line
				x1={todayX}
				x2={todayX}
				y1={plot.top}
				y2={plot.bottom}
				stroke="var(--color-text-muted)"
				strokeDasharray="4 5"
			/>
			<path
				d={bandFor(data.uncertainty.upper, data.uncertainty.lower, dates, plot)}
				fill={data.uncertainty.color}
				opacity=".7"
			/>
			{data.series.map((series) => (
				<path
					key={series.id}
					d={pathFor(series.points, dates, plot)}
					fill="none"
					stroke={series.color}
					strokeLinecap="round"
					strokeLinejoin="round"
					strokeWidth={series.strokeWidth ?? 2.5}
				/>
			))}
			<circle
				cx={todayX}
				cy={yFor(
					data.series[1]?.points.find((point) => point.date === data.today)
						?.value ?? 0,
					plot,
				)}
				r={mobile ? 5 : 6}
				fill="var(--color-primary)"
			/>
			<text
				x={plot.left}
				y={plot.top - 24}
				fill="var(--color-text-muted)"
				fontSize={mobile ? 11 : 12}
			>
				INR
			</text>
			{data.yAxisLabels.map((label) => (
				<text
					key={`y-${label.value}`}
					x={plot.left - 10}
					y={yFor(label.value, plot) + 4}
					textAnchor="end"
					fill="var(--color-text-muted)"
					fontSize={mobile ? 11 : 12}
				>
					{label.label}
				</text>
			))}
			<text
				x={todayX}
				y={plot.top - 10}
				textAnchor="middle"
				fill="var(--color-ink)"
				fontSize="13"
			>
				Today
			</text>
			<text
				x={plot.right}
				y={plot.top + 12}
				textAnchor="end"
				fill="var(--color-primary)"
				fontSize={mobile ? 11 : 13}
			>
				Above buffer through June
			</text>
			<text
				x={plot.right}
				y={yFor(data.buffer, plot) - 8}
				textAnchor="end"
				fill="var(--color-ink)"
				fontSize={mobile ? 11 : 13}
			>
				Buffer
			</text>
			{data.xAxisLabels
				.filter(
					(_, index) =>
						!mobile || index % 2 === 0 || index === data.xAxisLabels.length - 1,
				)
				.map((label) => (
					<text
						key={label.date}
						x={xFor(label.date, dates, plot)}
						y={plot.bottom + 25}
						textAnchor="middle"
						fill="var(--color-text-muted)"
						fontSize={mobile ? 10 : 12}
					>
						{label.label}
					</text>
				))}
		</svg>
	);
}

/** Renders the forecast using structured points rather than precomputed SVG paths. */
function DetailedForecastChart({ data }: { data: ForecastChartData }) {
	return (
		<div
			className="mt-8 w-full lg:mt-0"
			aria-label="Baseline cash flow forecast chart"
		>
			<div className="sm:hidden">
				<ChartSvg data={data} mobile />
			</div>
			<div className="hidden sm:block">
				<ChartSvg data={data} />
			</div>
			<div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-text-muted">
				{data.series.map((series) => (
					<span key={series.id} className="inline-flex items-center gap-2">
						<span
							className="h-0.5 w-6 rounded-full"
							style={{ backgroundColor: series.color }}
						/>
						{series.label}
					</span>
				))}
				<span className="inline-flex items-center gap-2">
					<span
						className="h-3 w-6 rounded-sm"
						style={{ backgroundColor: data.uncertainty.color }}
					/>
					Uncertainty
				</span>
				<span className="inline-flex items-center gap-2">
					<span className="h-0.5 w-6 border-t border-dashed border-ink" />
					Buffer
				</span>
			</div>
		</div>
	);
}

export default DetailedForecastChart;
