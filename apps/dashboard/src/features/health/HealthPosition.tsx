import { cn } from '@/utils/cn';
import type { HealthScore } from './types';

type HealthPositionProps = {
	scores: HealthScore[];
	healthDelta: string;
	healthDeltaValue: number;
	className?: string;
};

/** Renders the baseline and scenario health scores as aligned comparison bars. */
function HealthPosition({
	scores,
	healthDelta,
	healthDeltaValue,
	className,
}: HealthPositionProps) {
	const direction =
		healthDeltaValue > 0 ? '↑' : healthDeltaValue < 0 ? '↓' : '→';

	return (
		<section
			className={cn('mt-16 sm:mt-20 lg:mt-24', className)}
			aria-labelledby="health-position-title"
		>
			<h2
				id="health-position-title"
				className="font-serif text-2xl leading-tight text-ink sm:text-3xl"
			>
				Health position
			</h2>
			<p className="mt-2 max-w-md text-sm text-text-muted sm:text-base">
				Directional score change under the selected scenario.
			</p>

			<div className="mt-8 space-y-7" role="list" aria-label="Health scores">
				{scores.map((score) => (
					<div key={score.label} role="listitem">
						<div className="grid items-center gap-3 xl:grid-cols-[20rem_minmax(0,1fr)] xl:gap-5">
							<div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm sm:text-base">
								<span className="text-ink">{score.label}</span>
								<span className="tabular-nums text-2xl font-medium tracking-tight text-primary sm:text-3xl">
									{score.score}
								</span>
								<span className="text-primary" aria-hidden="true">
									•
								</span>
								<span className="text-primary">{score.status}</span>
							</div>
							<div
								className="h-4 overflow-hidden rounded-full bg-primary-soft/70 sm:h-[18px]"
								role="meter"
								aria-label={`${score.label} health score`}
								aria-valuemin={0}
								aria-valuemax={100}
								aria-valuenow={score.score}
							>
								<div
									className={`h-full rounded-full ${
										score.tone === 'primary' ? 'bg-primary' : 'bg-primary/60'
									}`}
									style={{ width: `${score.score}%` }}
								/>
							</div>
						</div>
					</div>
				))}
			</div>
			<p className="mt-6 flex items-center gap-3 text-sm font-medium text-primary sm:text-base xl:ml-[21.25rem]">
				<span className="text-xl leading-none" aria-hidden="true">
					{direction}
				</span>
				{healthDelta}
			</p>
		</section>
	);
}

export default HealthPosition;
