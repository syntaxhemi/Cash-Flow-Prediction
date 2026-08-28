import { cn } from '@/utils/cn';
import type { HealthStat } from './types';

type HealthStatsBarProps = {
	stats: HealthStat[];
};

/** Displays the Health page's open, four-column cash summary. */
function HealthStatsBar({ stats }: HealthStatsBarProps) {
	const statRows = Array.from(
		{ length: Math.ceil(stats.length / 2) },
		(_, rowIndex) => stats.slice(rowIndex * 2, rowIndex * 2 + 2),
	);

	return (
		<section
			className="mt-14 flex flex-col gap-8 sm:mt-16 sm:grid sm:grid-cols-4 sm:items-center sm:gap-4 lg:gap-8"
			aria-label="Cash position under selected scenario"
		>
			{statRows.map((row, rowIndex) => (
				<div
					key={rowIndex}
					className="flex min-w-0 justify-between gap-4 sm:contents"
				>
					{row.map((stat, columnIndex) => {
						const index = rowIndex * 2 + columnIndex;

						return (
							<div key={stat.label} className="min-w-0">
								<div className="flex flex-col gap-1">
									<p
										className={cn(
											'text-xs',
											index === 0
												? 'font-semibold uppercase tracking-[0.16em] text-primary'
												: 'text-sm text-text-muted',
										)}
									>
										{stat.label}
									</p>
									<p
										className={cn(
											'whitespace-nowrap tabular-nums tracking-tight',
											index === 0
												? 'text-4xl lg:text-5xl'
												: 'text-2xl lg:text-3xl',
											stat.tone === 'primary' ? 'text-primary' : 'text-ink',
										)}
									>
										{stat.value}
									</p>
								</div>
								{stat.supporting && (
									<p className="mt-1 text-xs leading-tight text-text-muted">
										{stat.supporting}
									</p>
								)}
							</div>
						);
					})}
				</div>
			))}
		</section>
	);
}

export default HealthStatsBar;
