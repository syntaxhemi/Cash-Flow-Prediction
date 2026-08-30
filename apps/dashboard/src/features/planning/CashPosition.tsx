function CashPosition() {
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
									₹1.58M
								</p>
							</div>
							<div className="absolute left-[39%] top-0 -translate-x-1/2 text-center">
								<p className="text-xs text-simulation">Operating buffer</p>
								<p className="mt-1 font-serif text-base tabular-nums text-simulation sm:text-2xl">
									₹1.60M
								</p>
							</div>
							<div className="absolute right-0 top-0 text-right">
								<p className="text-xs text-text-muted">Draft scenario</p>
								<p className="mt-1 font-serif text-base tabular-nums text-ink sm:text-2xl">
									₹2.20M
								</p>
							</div>
						</div>
						<div
							className="relative mt-4 h-2 rounded-full bg-border"
							role="img"
							aria-label="Cash position moves from a baseline of 1.58 million rupees past the 1.60 million rupee operating buffer to a draft scenario of 2.20 million rupees"
						>
							<span className="absolute inset-y-0 left-[39%] right-0 rounded-full bg-primary" />
							<span className="absolute left-[36%] top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-text-muted" />
							<span className="absolute left-[39%] top-1/2 h-6 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-simulation" />
							<span className="absolute right-0 top-1/2 size-4 -translate-y-1/2 translate-x-1/2 rounded-full border-2 border-surface bg-primary" />
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
						+₹620K
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
