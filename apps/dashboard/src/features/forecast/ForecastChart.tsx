// @ts-nocheck
import type { ForecastChartData } from './types';

type ForecastChartProps = { data: ForecastChartData };

function ForecastChart({ data }: ForecastChartProps) {
	const chartLines = (
		<>
			<line x1="40" y1="184" x2="960" y2="184" stroke="var(--color-border)" />
			<line
				x1="40"
				y1="132"
				x2="960"
				y2="132"
				stroke="var(--color-ink)"
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
			<path
				d={data.confidenceBand}
				fill={data.confidenceBandColor}
				opacity="0.7"
			/>
			{data.traces.map((trace) => (
				<path
					key={trace.color}
					d={trace.path}
					fill="none"
					stroke={trace.color}
					strokeLinecap="round"
					strokeWidth={trace.strokeWidth ?? 3}
				/>
			))}
			<circle
				cx={data.today.x}
				cy={data.today.y}
				r="6"
				fill="var(--color-primary)"
			/>
		</>
	);

	return (
		<div
			className="mt-8 w-full lg:mt-0"
			aria-label="Baseline cash flow forecast chart"
		>
			<svg
				className="h-auto w-full sm:hidden"
				viewBox="0 0 350 220"
				role="img"
				aria-labelledby="forecast-mobile-title forecast-mobile-description"
			>
				<title id="forecast-mobile-title">Baseline forecast</title>
				<desc id="forecast-mobile-description">
					Recorded cash flow transitions into a baseline forecast that remains
					above the buffer through June.
				</desc>
				<g transform="scale(0.34 1)">{chartLines}</g>
				{data.yAxisLabels.map(({ label, y }) => (
					<text
						key={`mobile-y-${label}`}
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
						key={`mobile-annotation-${label}`}
						x="249"
						y={48 + index * 15}
						fill="var(--color-primary)"
						fontSize="12"
					>
						{label}
					</text>
				))}
				<text x="249" y="108" fill="var(--color-ink)" fontSize="12">
					{data.annotations.buffer}
				</text>
				{data.mobileXAxisLabels.map(({ label, x }) => (
					<text
						key={`mobile-x-${label}`}
						x={x}
						y="202"
						textAnchor="middle"
						fill="var(--color-text-muted)"
						fontSize="10"
					>
						{label}
					</text>
				))}
			</svg>
			<svg
				className="hidden h-56 w-full sm:block"
				viewBox="0 0 1440 192"
				role="img"
				aria-labelledby="forecast-title forecast-description"
			>
				<title id="forecast-title">Baseline forecast</title>
				<desc id="forecast-description">
					Recorded cash flow transitions into a baseline forecast that remains
					above the buffer through June.
				</desc>
				<g transform="scale(1.44 0.768)">{chartLines}</g>
				{data.yAxisLabels.map(({ label, y }) => (
					<text
						key={`desktop-y-${label}`}
						x="49"
						y={y}
						textAnchor="end"
						fill="var(--color-text-muted)"
						fontSize="12"
					>
						{label}
					</text>
				))}
				<text x="49" y="38" fill="var(--color-text-muted)" fontSize="12">
					INR
				</text>
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
						key={`desktop-annotation-${label}`}
						x="1260"
						y={41 + index * 14}
						fill="var(--color-primary)"
						fontSize="13"
					>
						{label}
					</text>
				))}
				<text x="1260" y="98" fill="var(--color-ink)" fontSize="13">
					{data.annotations.buffer}
				</text>
				{data.xAxisLabels.map(({ label, x }) => (
					<text
						key={`desktop-x-${label}`}
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
			<div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-text-muted">
				<span className="inline-flex items-center gap-2">
					<span className="h-0.5 w-6 rounded-full bg-ink" aria-hidden="true" />
					Recorded
				</span>
				<span className="inline-flex items-center gap-2">
					<span
						className="h-0.5 w-6 rounded-full bg-primary"
						aria-hidden="true"
					/>
					Baseline
				</span>
				<span className="inline-flex items-center gap-2">
					<span
						className="h-3 w-6 rounded-sm bg-primary-soft"
						aria-hidden="true"
					/>
					Uncertainty
				</span>
				<span className="inline-flex items-center gap-2">
					<span
						className="h-0.5 w-6 border-t border-dashed border-ink"
						aria-hidden="true"
					/>
					Buffer
				</span>
			</div>
		</div>
	);
}

export default ForecastChart;
