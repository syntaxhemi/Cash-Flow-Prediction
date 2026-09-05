import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/formatCurrency';
import type { PlanningOption } from './types';

function MitigationDetails({ option }: { option: PlanningOption }) {
	return (
		<div
			className={cn(
				'min-w-0 py-2 sm:py-3',
				option.recommended &&
					'-ml-4 rounded-control bg-primary-soft/45 px-4 sm:-ml-5 sm:px-5 lg:ml-0',
			)}
		>
			<div className="flex flex-wrap items-start justify-between gap-x-5 gap-y-3">
				<div className="min-w-0">
					<h3 className="font-serif text-[21px] leading-tight text-ink sm:text-2xl">
						{option.name}
					</h3>
					<p className="mt-1 text-sm tabular-nums text-text-muted">
						{option.detail}
					</p>
					<a
						href={option.linkHref}
						className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline"
					>
						{option.link}
						<span aria-hidden="true">→</span>
					</a>
				</div>
				<div className="shrink-0 text-left sm:min-w-36 sm:pt-1">
					<p className="text-sm tabular-nums text-ink">
						{formatCurrency(option.postScenario)}{' '}
						<span className="text-text-muted">projected cash</span>
					</p>
					<span className="mt-3 inline-flex rounded-full bg-primary-soft px-2.5 py-1 text-xs font-medium text-primary">
						{option.meetsBuffer
							? 'Above operating buffer'
							: 'Below operating buffer'}
					</span>
				</div>
			</div>
		</div>
	);
}

function MitigationOptionBlock({ option }: { option: PlanningOption }) {
	return (
		<div className="min-w-0">
			<MitigationDetails option={option} />
			{option.recommended && (
				<span className="mx-auto mt-2 flex w-fit rounded-control border border-primary/20 bg-primary-soft px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-primary">
					Recommended draft
				</span>
			)}
		</div>
	);
}

export function DesktopMitigationSpectrum({
	options,
}: {
	options: PlanningOption[];
}) {
	return (
		<div
			className="hidden lg:block"
			aria-label="Mitigation options by cash impact"
		>
			<div className="grid grid-cols-[6.5rem_minmax(0,1fr)_6.5rem] items-center">
				<span className="text-xs text-text-muted">Lower impact</span>
				<div className="relative h-14">
					<div className="absolute inset-x-0 top-9 h-px bg-text-muted/45" />
					{options.map((option, index) => (
						<div
							key={option.name}
							className="absolute top-0 -translate-x-1/2 text-center"
							style={{
								left: `${((index + 0.5) / Math.max(options.length, 1)) * 100}%`,
							}}
						>
								<p className="font-serif text-lg text-primary">
									{option.impact >= 0 ? '+' : '−'}
									{formatCurrency(Math.abs(option.impact))}
								</p>
							<span
								className={cn(
									'mx-auto mt-1 block h-5 w-1 rounded-full',
									option.recommended ? 'bg-primary' : 'bg-primary/80',
								)}
							/>
						</div>
					))}
				</div>
				<span className="text-right text-xs text-text-muted">
					Higher impact
				</span>
			</div>
			<div className="grid grid-cols-[6.5rem_minmax(0,1fr)_6.5rem]">
				<div
					className="col-start-2 grid"
					style={{
						gridTemplateColumns: `repeat(${Math.max(options.length, 1)}, minmax(0, 1fr))`,
					}}
				>
					{options.map((option) => (
						<MitigationOptionBlock key={option.name} option={option} />
					))}
				</div>
			</div>
		</div>
	);
}

export function MobileMitigationSpectrum({
	options,
}: {
	options: PlanningOption[];
}) {
	return (
		<div className="lg:hidden" aria-label="Mitigation options by cash impact">
			<div className="relative">
				<div className="absolute bottom-0 left-[1.5rem] top-0 w-px bg-border" />
				<span className="absolute left-0 top-0 w-[4.5rem] -translate-y-full text-left text-[11px] text-text-muted">
					Lower impact
				</span>
				<span className="absolute bottom-0 left-0 w-[4.5rem] translate-y-full text-left text-[11px] text-text-muted">
					Higher impact
				</span>
				<div className="space-y-5">
					{options.map((option) => (
						<div
							key={option.name}
							className="grid grid-cols-[4.5rem_minmax(0,1fr)] items-center gap-x-2"
						>
							<div className="relative -left-3 z-10 flex flex-col items-center gap-1 text-center">
								<span className="font-serif text-base text-primary">
									{option.impact >= 0 ? '+' : '−'}
									{formatCurrency(Math.abs(option.impact))}
								</span>
								<span
									className={cn(
										'size-4 rounded-full border-2 border-surface bg-text-muted',
										option.recommended && 'bg-primary',
									)}
								/>
							</div>
							<MitigationOptionBlock option={option} />
						</div>
					))}
				</div>
			</div>
		</div>
	);
}
