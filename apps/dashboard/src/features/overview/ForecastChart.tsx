import type { ForecastChartData } from './types';

type ForecastChartProps = {
	data: ForecastChartData;
};

function ForecastChart({ data }: ForecastChartProps) {
	return (
		<div
			className="mx-auto mt-8 w-full max-w-5xl overflow-hidden"
			aria-label="Cash flow forecast chart"
		>
			<svg
				viewBox="0 0 350 220"
				className="h-56 w-full sm:hidden"
				role="img"
				aria-labelledby="forecast-chart-mobile-title forecast-chart-mobile-description"
			>
				<title id="forecast-chart-mobile-title">Cash flow outlook</title>
				<desc id="forecast-chart-mobile-description">
					Responsive mobile cash flow outlook with historical and forecast
					values.
				</desc>
				<g transform="scale(0.34 1)">
					<line
						x1="40"
						y1="184"
						x2="960"
						y2="184"
						stroke="var(--color-border)"
					/>
					<line
						x1="40"
						y1="132"
						x2="960"
						y2="132"
						stroke="var(--color-border)"
						strokeDasharray="4 5"
					/>
					<line x1="40" y1="80" x2="960" y2="80" stroke="var(--color-border)" />
					<line
						x1="555"
						y1="24"
						x2="555"
						y2="184"
						stroke="var(--color-text-muted)"
						strokeDasharray="4 5"
					/>
					{data.traces.map((trace) => (
						<path
							key={`mobile-${trace.color}-${trace.path}`}
							d={trace.path}
							fill={trace.fill ?? 'none'}
							stroke={trace.color}
							strokeLinecap="round"
							strokeWidth={trace.strokeWidth ?? 3}
							opacity={trace.opacity}
						/>
					))}
					<path
						d={data.confidenceBand}
						fill={data.confidenceBandColor}
						opacity="0.7"
					/>
					<circle
						cx={data.today.x}
						cy={data.today.y}
						r="6"
						fill="var(--color-primary)"
					/>
				</g>
				{data.yAxisLabels.map(({ label, y }) => (
					<text
						key={`mobile-${label}`}
						x="37"
						y={y}
						textAnchor="end"
						fill="var(--color-text-muted)"
						fontSize="12"
					>
						{label}
					</text>
				))}
				<text
					x="189"
					y="16"
					textAnchor="middle"
					fill="var(--color-ink)"
					fontSize="13"
				>
					Today
				</text>
				{data.annotations.aboveBuffer.map((label, index) => (
					<text
						key={`mobile-${label}`}
						x="250"
						y={48 + index * 15}
						fill="var(--color-primary)"
						fontSize="12"
					>
						{label}
					</text>
				))}
				<text x="250" y="108" fill="var(--color-ink)" fontSize="12">
					{data.annotations.buffer}
				</text>
				{data.mobileXAxisLabels.map(({ label, x }) => (
					<text
						key={`mobile-${label}`}
						x={x}
						y="202"
						textAnchor="middle"
						fill="var(--color-text-muted)"
						fontSize="11"
					>
						{label}
					</text>
				))}
			</svg>
			<svg
				viewBox="0 0 1440 192"
				className="hidden h-48 w-full sm:block"
				role="img"
				aria-labelledby="forecast-chart-title forecast-chart-description"
			>
				<title id="forecast-chart-title">Cash flow outlook</title>
				<desc id="forecast-chart-description">
					Historical cash flow transitions into a baseline forecast that remains
					above the buffer.
				</desc>
				<g transform="scale(1.44 0.768)">
					<line
						x1="40"
						y1="184"
						x2="960"
						y2="184"
						stroke="var(--color-border)"
					/>
					<line
						x1="40"
						y1="132"
						x2="960"
						y2="132"
						stroke="var(--color-border)"
						strokeDasharray="4 5"
					/>
					<line x1="40" y1="80" x2="960" y2="80" stroke="var(--color-border)" />
					<line
						x1="555"
						y1="24"
						x2="555"
						y2="184"
						stroke="var(--color-text-muted)"
						strokeDasharray="4 5"
					/>
					{data.traces.map((trace) => (
						<path
							key={`${trace.color}-${trace.path}`}
							d={trace.path}
							fill={trace.fill ?? 'none'}
							stroke={trace.color}
							strokeLinecap="round"
							strokeWidth={trace.strokeWidth ?? 3}
							opacity={trace.opacity}
						/>
					))}
					<path
						d={data.confidenceBand}
						fill={data.confidenceBandColor}
						opacity="0.7"
					/>
					<circle
						cx={data.today.x}
						cy={data.today.y}
						r="6"
						fill="var(--color-primary)"
					/>
				</g>
				{data.yAxisLabels.map(({ label, y }) => (
					<text
						key={label}
						x="49"
						y={y}
						textAnchor="end"
						fill="var(--color-text-muted)"
						fontSize="12"
					>
						{label}
					</text>
				))}
				<text
					x="799"
					y="12"
					textAnchor="middle"
					fill="var(--color-ink)"
					fontSize="13"
				>
					Today
				</text>
				{data.annotations.aboveBuffer.map((label, index) => (
					<text
						key={label}
						x="1350"
						y={41 + index * 14}
						fill="var(--color-primary)"
						fontSize="13"
					>
						{label}
					</text>
				))}
				<text x="1350" y="98" fill="var(--color-ink)" fontSize="13">
					{data.annotations.buffer}
				</text>
				{data.xAxisLabels.map(({ label, x }) => (
					<text
						key={label}
						x={x}
						y="178"
						textAnchor="middle"
						fill="var(--color-text-muted)"
						fontSize="12"
					>
						{label}
					</text>
				))}
			</svg>
		</div>
	);
}

export default ForecastChart;
