type CashMovementProps = {
	inflows: string;
	outflows: string;
	inflowsValue: number;
	outflowsValue: number;
	detail: string;
};

function CashMovement({
	inflows,
	outflows,
	inflowsValue,
	outflowsValue,
	detail,
}: CashMovementProps) {
	const maximum = Math.max(inflowsValue, outflowsValue, 1);
	const inflowWidth = `${(inflowsValue / maximum) * 100}%`;
	const outflowWidth = `${(outflowsValue / maximum) * 100}%`;

	return (
		<section aria-labelledby="cash-movement-title">
			<h2 id="cash-movement-title" className="font-serif text-2xl text-ink">
				Cash movement
			</h2>
			<div className="mt-6 space-y-4">
				<div className="flex items-center gap-4 text-sm">
					<span className="w-32 shrink-0 text-ink">Expected inflows</span>
					<span className="h-2 flex-1" aria-hidden="true">
						<span
							className="block h-full rounded-full bg-primary"
							style={{ width: inflowWidth }}
						/>
					</span>
					<span className="tabular-nums text-ink">{inflows}</span>
				</div>
				<div className="flex items-center gap-4 text-sm">
					<span className="w-32 shrink-0 text-ink">Expected outflows</span>
					<span className="h-2 flex-1" aria-hidden="true">
						<span
							className="block h-full rounded-full bg-primary"
							style={{ width: outflowWidth }}
						/>
					</span>
					<span className="ml-auto tabular-nums text-ink">{outflows}</span>
				</div>
			</div>
			<p className="mt-5 text-sm text-text-muted">{detail}</p>
		</section>
	);
}

export default CashMovement;
