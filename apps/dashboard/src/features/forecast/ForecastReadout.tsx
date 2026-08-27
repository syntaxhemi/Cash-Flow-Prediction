function ForecastReadout() {
	return (
		<aside
			className="mt-12 lg:mt-0 lg:self-stretch lg:border-l lg:border-border lg:pl-12"
			aria-labelledby="forecast-readout-title"
		>
			<p className="text-xs font-semibold uppercase tracking-widest text-primary">
				Forecast readout
			</p>
			<h2
				id="forecast-readout-title"
				className="mt-5 max-w-sm font-serif text-3xl leading-tight text-ink"
			>
				The baseline stays clear of the buffer.
			</h2>
			<p className="mt-5 max-w-sm text-base leading-relaxed text-text-muted">
				The projected path improves gradually as receivables convert.
			</p>
			<a
				href="/receivables"
				className="mt-6 inline-flex border-b border-transparent pb-px text-sm font-medium text-primary no-underline hover:border-primary"
			>
				Open forecast explanation{' '}
				<span className="ml-2" aria-hidden="true">
					→
				</span>
			</a>
		</aside>
	);
}

export default ForecastReadout;
