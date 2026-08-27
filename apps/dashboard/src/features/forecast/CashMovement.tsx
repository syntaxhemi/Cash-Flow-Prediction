function CashMovement() {
	return (
		<section aria-labelledby="cash-movement-title">
			<h2 id="cash-movement-title" className="font-serif text-2xl text-ink">
				Cash movement
			</h2>
			<div className="mt-6 space-y-4">
				<div className="flex items-center gap-4 text-sm">
					<span className="w-32 shrink-0 text-ink">Expected inflows</span>
					<span
						className="h-2 flex-1 rounded-full bg-primary"
						aria-hidden="true"
					/>
					<span className="tabular-nums text-ink">₹312K</span>
				</div>
				<div className="flex items-center gap-4 text-sm">
					<span className="w-32 shrink-0 text-ink">Expected outflows</span>
					<span
						className="h-2 w-2/5 rounded-full bg-primary-soft"
						aria-hidden="true"
					/>
					<span className="ml-auto tabular-nums text-ink">₹128K</span>
				</div>
			</div>
			<p className="mt-5 text-sm text-text-muted">
				Receivables drive most of the projected improvement.
			</p>
		</section>
	);
}

export default CashMovement;
