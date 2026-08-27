import type { ForecastImpact } from './types';

type ForecastImpactGridProps = { impacts: ForecastImpact[] };

function ForecastImpactGrid({ impacts }: ForecastImpactGridProps) {
	return (
		<section aria-labelledby="forecast-impact-title">
			<h2 id="forecast-impact-title" className="font-serif text-2xl text-ink">
				What changes the forecast
			</h2>
			<div className="mt-6 grid gap-4 sm:grid-cols-2">
				{impacts.map((impact) => (
					<article
						key={impact.label}
						className={
							impact.featured
								? 'rounded-card bg-primary-soft p-5 sm:col-span-2'
								: 'rounded-card bg-canvas p-5'
						}
					>
						<p className="text-xs font-semibold uppercase tracking-widest text-primary">
							{impact.label}
						</p>
						<p className="mt-3 font-serif text-3xl leading-none text-primary">
							{impact.amount}
						</p>
						<p className="mt-3 text-sm text-text-muted">{impact.detail}</p>
					</article>
				))}
			</div>
		</section>
	);
}

export default ForecastImpactGrid;
