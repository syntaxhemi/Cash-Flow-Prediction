import { FiActivity } from 'react-icons/fi';
import type { ForecastRun } from './types';

type ForecastRunsProps = {
	runs: ForecastRun[];
	baselineSnapshot: string;
};

function ForecastRuns({ runs, baselineSnapshot }: ForecastRunsProps) {
	const [baselineTitle, ...baselineRest] = baselineSnapshot.split(' ');
	const baselineDetail = baselineRest.join(' ');

	return (
		<section
			className="border-t-0 pt-0 lg:border-t lg:border-border lg:pt-6"
			aria-label="Forecast runs"
		>
			<div className="flex flex-col gap-4 text-sm lg:flex-row lg:items-center">
				<div className="flex items-center gap-3 font-serif text-2xl text-ink lg:hidden">
					<FiActivity
						className="size-6 shrink-0 text-primary"
						aria-hidden="true"
					/>
					<span>Forecast runs</span>
				</div>
				<div className="hidden shrink-0 items-center gap-3 pr-6 font-medium text-ink lg:flex">
					<FiActivity className="size-5 text-primary" aria-hidden="true" />
					<span>Forecast runs</span>
				</div>
				<div className="flex w-full flex-nowrap items-center justify-between lg:contents">
					{runs.map((run, index) => (
						<p
							key={run.label}
							className={`whitespace-nowrap pr-2 text-text-muted lg:pr-6 ${
								index > 0 ? 'border-l border-border pl-2 lg:pl-6' : 'pl-0'
							}`}
						>
							<span
								className={`${
									run.label === 'Latest run'
										? 'font-medium text-primary'
										: 'font-medium text-text-muted'
								} block lg:inline`}
							>
								{run.label}
							</span>
							<span className="hidden lg:inline" aria-hidden="true">
								{' · '}
							</span>
							<span className="block lg:inline">{run.time}</span>
						</p>
					))}
					<p className="whitespace-nowrap border-l border-border px-2 text-text-muted lg:px-6">
						<span className="block lg:inline">{baselineTitle}</span>{' '}
						<span className="block lg:inline">{baselineDetail}</span>
					</p>
					<a
						href="/forecast"
						className="ml-auto hidden border-b border-transparent pb-px font-medium text-primary no-underline hover:border-primary lg:inline-flex"
					>
						View history{' '}
						<span className="ml-2" aria-hidden="true">
							→
						</span>
					</a>
				</div>
			</div>
			<a
				href="/forecast"
				className="mt-6 flex justify-center border-b border-transparent pb-px text-sm font-medium text-primary no-underline hover:border-primary lg:hidden"
			>
				View history{' '}
				<span className="ml-2" aria-hidden="true">
					→
				</span>
			</a>
		</section>
	);
}

export default ForecastRuns;
