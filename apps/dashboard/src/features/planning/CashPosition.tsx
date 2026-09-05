import { formatCurrency } from '@/utils/formatCurrency';

type CashPositionProps = {
	baseline: number;
	buffer: number;
	draft: number | null;
};

function markerPosition(value: number, minimum: number, span: number) {
	return `${((value - minimum) / span) * 100}%`;
}

function CashPosition({ baseline, buffer, draft }: CashPositionProps) {
	const draftValue = draft ?? baseline;
	const minimum = Math.min(0, baseline, buffer, draftValue);
	const maximum = Math.max(baseline, buffer, draftValue, 1);
	const span = Math.max(maximum - minimum, 1);
	const baselinePosition = markerPosition(baseline, minimum, span);
	const bufferPosition = markerPosition(buffer, minimum, span);
	const draftPosition = markerPosition(draftValue, minimum, span);
	const baselinePercent = Number.parseFloat(baselinePosition);
	const bufferPercent = Number.parseFloat(bufferPosition);
	const draftPercent = Number.parseFloat(draftPosition);
	const baselineLabel = formatCurrency(baseline);
	const bufferLabel = formatCurrency(buffer);
	const bufferLabelIsNearEdgeLabel =
		bufferPercent < 28 || bufferPercent > 72;
	const bufferLabelIsNearAnotherValue =
		baselineLabel === bufferLabel ||
		bufferLabelIsNearEdgeLabel;
	const improvement = draftValue - baseline;

	return (
		<section className="mt-12 sm:mt-14" aria-labelledby="cash-position-title">
			<p
				id="cash-position-title"
				className="text-xs font-semibold uppercase tracking-[0.14em] text-primary"
			>
				Cash position after this draft
			</p>
			<div className="mt-5 grid gap-7 lg:grid-cols-[minmax(0,1fr)_14rem] lg:items-center lg:gap-14">
				<div>
					<div className="relative pt-[4.25rem]">
						<div className="absolute inset-x-0 top-0 h-14">
							<div className="absolute left-0 top-0">
								<p className="text-xs text-text-muted">Baseline</p>
								<p className="mt-1 font-serif text-base tabular-nums text-ink sm:text-2xl">
									{baselineLabel}
								</p>
							</div>
							{!bufferLabelIsNearAnotherValue ? (
								<div
									className="absolute top-0 -translate-x-1/2 text-center"
									style={{ left: bufferPosition }}
								>
									<p className="text-xs text-simulation">Operating buffer</p>
									<p className="mt-1 font-serif text-base tabular-nums text-simulation sm:text-2xl">
									{bufferLabel}
									</p>
								</div>
							) : null}
							<div className="absolute right-0 top-0 text-right">
								<p className="text-xs text-text-muted">Draft scenario</p>
								<p className="mt-1 font-serif text-base tabular-nums text-ink sm:text-2xl">
									{formatCurrency(draftValue)}
								</p>
							</div>
						</div>
						<div
							className="relative mt-4 h-2 rounded-full bg-border"
							role="img"
							aria-label={`Cash position moves from a baseline of ${formatCurrency(baseline)} to a draft scenario of ${formatCurrency(draftValue)} against an operating buffer of ${formatCurrency(buffer)}`}
						>
							<span
								className="absolute inset-y-0 rounded-full bg-primary"
								style={{
									left: `${Math.min(baselinePercent, draftPercent)}%`,
									width: `${Math.abs(draftPercent - baselinePercent)}%`,
								}}
							/>
							<span
								className="absolute top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-text-muted"
								style={{ left: baselinePosition }}
							/>
							<span
								className="absolute top-1/2 h-6 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-simulation"
								style={{ left: bufferPosition }}
							/>
							<span
								className="absolute top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-primary"
								style={{ left: draftPosition }}
							/>
						</div>
						<div className="mt-8 flex flex-wrap justify-start gap-x-3 gap-y-2 text-xs text-text-muted sm:justify-center sm:gap-x-10">
							<span className="inline-flex items-center gap-2">
								<span className="size-2.5 rounded-full bg-text-muted/50" />
								Baseline
							</span>
							<span className="inline-flex items-center gap-2">
								<span className="size-2.5 rounded-full bg-simulation" />
								Operating buffer
							</span>
							<span className="inline-flex items-center gap-2">
								<span className="size-2.5 rounded-full bg-primary" />
								Draft scenario
							</span>
						</div>
					</div>
				</div>
				<div className="text-center lg:ml-4 lg:text-left">
					<p className="font-serif text-2xl tabular-nums text-primary sm:text-4xl">
						{improvement >= 0 ? '+' : '−'}
						{formatCurrency(Math.abs(improvement))}
					</p>
					<p className="mt-1 text-sm text-text-muted">
						improvement vs baseline
					</p>
				</div>
			</div>
		</section>
	);
}

export default CashPosition;
