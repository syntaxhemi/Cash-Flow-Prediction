function EnterpriseContext() {
	return (
		<div className="mb-10 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
			<span className="font-medium text-ink">Northstar Manufacturing</span>
			<span className="hidden text-text-muted sm:inline" aria-hidden="true">
				•
			</span>
			<span className="text-text-muted">Updated 8 minutes ago</span>
			<span className="text-text-muted" aria-hidden="true">
				•
			</span>
			<button
				type="button"
				className="font-medium text-primary underline-offset-4 hover:underline"
			>
				Run forecast
			</button>
		</div>
	);
}

export default EnterpriseContext;
