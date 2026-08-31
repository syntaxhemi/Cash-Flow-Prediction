import { cn } from '@/utils/cn';
import type { HealthImpact } from './types';

type HealthImpactCardsProps = {
	impacts: HealthImpact[];
	description?: string;
	className?: string;
};

const impactSurface = {
	featured: 'bg-primary-soft',
	neutral: 'bg-canvas',
	soft: 'bg-primary-soft/50',
} as const;

/** Presents the three observed drivers behind the latest forecast result. */
function HealthImpactCards({
	impacts,
	description = 'Observed drivers across the forecast window.',
	className,
}: HealthImpactCardsProps) {
	return (
		<section
			className={cn('mt-16 sm:mt-20 lg:mt-24', className)}
			aria-labelledby="health-impact-title"
		>
			<h2
				id="health-impact-title"
				className="font-serif text-2xl leading-tight text-ink sm:text-3xl"
			>
				What changed the result
			</h2>
			<p className="mt-2 text-sm text-text-muted sm:text-base">{description}</p>
			<div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4">
				{impacts.map((impact) => (
					<article
						key={impact.label}
						className={cn(
							'rounded-card p-4 sm:p-5',
							impactSurface[impact.tone],
							impact.tone === 'featured' && 'col-span-full',
						)}
					>
						<p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-primary sm:text-xs">
							{impact.label}
						</p>
						<div className="mt-3 grid grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] items-center gap-3 sm:gap-5">
							<p className="font-serif text-xl leading-none text-primary sm:text-2xl">
								{impact.amount}
							</p>
							<div>
								<p className="font-serif text-base leading-tight text-ink sm:text-lg">
									{impact.title}
								</p>
								<p className="mt-1 text-[11px] text-text-muted sm:text-xs">
									{impact.detail}
								</p>
							</div>
						</div>
					</article>
				))}
			</div>
		</section>
	);
}

export default HealthImpactCards;
