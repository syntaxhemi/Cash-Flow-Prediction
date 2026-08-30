import type { ForecastChartData, ForecastPoint } from './types';
import { formatCurrency } from '@/utils/formatCurrency';

type Plot = { left: number; right: number; top: number; bottom: number };

function xFor(date: string, dates: string[], plot: Plot) {
	const firstDate = Date.parse(dates[0] ?? date);
	const lastDate = Date.parse(dates.at(-1) ?? date);
	const range = Math.max(lastDate - firstDate, 1);
	const position = Math.min(Math.max(Date.parse(date) - firstDate, 0), range);
	return plot.left + (position / range) * (plot.right - plot.left);
}

function yFor(value: number, plot: Plot, minimum: number, maximum: number) {
	return (
		plot.top +
		((maximum - value) / Math.max(maximum - minimum, 1)) *
			(plot.bottom - plot.top)
	);
}

function pathFor(
	points: ForecastPoint[],
	dates: string[],
	plot: Plot,
	minimum: number,
	maximum: number,
) {
	return points
		.map(
			(point, index) =>
				`${index ? 'L' : 'M'} ${xFor(point.date, dates, plot)} ${yFor(point.value, plot, minimum, maximum)}`,
		)
		.join(' ');
}

function bandFor(
	upper: ForecastPoint[],
	lower: ForecastPoint[],
	dates: string[],
	plot: Plot,
	minimum: number,
	maximum: number,
) {
	return `${pathFor(upper, dates, plot, minimum, maximum)} ${lower
		.slice()
		.reverse()
		.map(
			(point) =>
				`L ${xFor(point.date, dates, plot)} ${yFor(point.value, plot, minimum, maximum)}`,
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
	const dates = [
		...new Set(
			data.series.flatMap((series) => series.points).map((point) => point.date),
		),
	].sort();
	const targetStart = data.targetPeriod?.start ?? data.today;
	const targetEnd = data.targetPeriod?.end ?? data.today;
	const forecastValue =
		data.forecastValue ?? data.series[1]?.points.at(-1)?.value ?? 0;
	const axisValues = data.yAxisLabels.map((label) => label.value);
	const minimum = Math.min(...axisValues);
	const maximum = Math.max(...axisValues);
	const todayX = xFor(targetStart, dates, plot);
	const targetEndX = xFor(targetEnd, dates, plot);
	return (
		<svg
			viewBox={`0 0 ${width} ${height}`}
			className="h-auto w-full"
			role="img"
			aria-label="Detailed baseline cash flow forecast"
		>
			<rect
				x={todayX}
				y={plot.top}
				width={Math.max(targetEndX - todayX, 0)}
				height={plot.bottom - plot.top}
				fill="var(--color-primary-soft)"
				opacity=".35"
			/>
			{data.yAxisLabels.map((label) => {
				const y = yFor(label.value, plot, minimum, maximum);
				return (
					<line
						key={label.value}
						x1={plot.left}
						x2={plot.right}
						y1={y}
						y2={y}
						stroke="var(--color-border)"
					/>
				);
			})}
			<line
				x1={plot.left}
				x2={plot.right}
				y1={yFor(data.buffer, plot, minimum, maximum)}
				y2={yFor(data.buffer, plot, minimum, maximum)}
				stroke="var(--color-ink)"
				strokeDasharray="5 6"
			/>
			<line
				x1={todayX}
				x2={todayX}
				y1={plot.top}
				y2={plot.bottom}
				stroke="var(--color-text-muted)"
				strokeDasharray="4 5"
			/>
			{data.uncertainty ? (
				<path
					d={bandFor(
						data.uncertainty.upper,
						data.uncertainty.lower,
						dates,
						plot,
						minimum,
						maximum,
					)}
					fill={data.uncertainty.color}
					opacity=".7"
				/>
			) : null}
			{data.series.map((series) => (
				<path
					key={series.id}
					d={pathFor(series.points, dates, plot, minimum, maximum)}
					fill="none"
					stroke={series.color}
					strokeLinecap="round"
					strokeLinejoin="round"
					strokeWidth={series.strokeWidth ?? 2.5}
				/>
			))}
			<circle
				cx={targetEndX}
				cy={yFor(forecastValue, plot, minimum, maximum)}
				r={mobile ? 5 : 6}
				fill="var(--color-primary)"
			/>
			<text
				x={targetEndX - 8}
				y={yFor(forecastValue, plot, minimum, maximum) - 10}
				textAnchor="end"
				fill="var(--color-primary)"
				fontSize={mobile ? 10 : 12}
			>
				{formatCurrency(forecastValue)}
			</text>
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
					y={yFor(label.value, plot, minimum, maximum) + 4}
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
				Forecast starts
			</text>
			<text
				x={plot.right}
				y={plot.top + 12}
				textAnchor="end"
				fill="var(--color-primary)"
				fontSize={mobile ? 11 : 13}
			>
				{data.annotations.aboveBuffer.join(' ')}
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
				{data.uncertainty ? (
					<span className="inline-flex items-center gap-2">
						<span
							className="h-3 w-6 rounded-sm"
							style={{ backgroundColor: data.uncertainty.color }}
						/>
						Uncertainty
					</span>
				) : null}
				<span className="inline-flex items-center gap-2">
					<span className="h-0.5 w-6 border-t border-dashed border-ink" />
					Buffer
				</span>
			</div>
		</div>
	);
}

export default DetailedForecastChart;
