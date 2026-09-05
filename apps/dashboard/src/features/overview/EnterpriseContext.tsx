import { Link } from 'react-router-dom';

type EnterpriseContextProps = {
	enterpriseName: string;
	updatedAt: string | null;
	hasForecast: boolean;
};

function EnterpriseContext({
	enterpriseName,
	updatedAt,
	hasForecast,
}: EnterpriseContextProps) {
	const updatedLabel = updatedAt
		? `Updated ${new Date(updatedAt).toLocaleString('en-IN', {
				dateStyle: 'medium',
				timeStyle: 'short',
		  })}`
		: 'Forecast not run yet';

	return (
		<div className="mb-10 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
			<span className="font-medium text-ink">{enterpriseName}</span>
			<span className="hidden text-text-muted sm:inline" aria-hidden="true">
				•
			</span>
			<span className="text-text-muted">{updatedLabel}</span>
			<span className="text-text-muted" aria-hidden="true">
				•
			</span>
			<Link
				to={hasForecast ? '/forecast' : '/data'}
				className="font-medium text-primary underline-offset-4 hover:underline"
			>
				{hasForecast ? 'Run forecast' : 'Connect data'}
			</Link>
		</div>
	);
}

export default EnterpriseContext;
