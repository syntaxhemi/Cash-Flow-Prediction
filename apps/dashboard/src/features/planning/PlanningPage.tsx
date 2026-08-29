import PageLayout from '@/components/layout/PageLayout';
import Button from '@/components/ui/Button';
import { cn } from '@/utils/cn';

type MitigationOption = {
	name: string;
	impact: string;
	detail: string;
	link: string;
	postScenario: string;
	linkHref: string;
	recommended?: boolean;
};

const mitigationOptions: MitigationOption[] = [
	{
		name: 'Tighten operating spend',
		impact: '+₹120K',
		detail: '₹6.35M / mo → ₹6.05M / mo',
		link: 'Review assumption',
		linkHref: '#operating-spend',
		postScenario: '₹1.70M',
	},
	{
		name: 'Defer discretionary capex',
		impact: '+₹180K',
		detail: '₹1.20M → ₹0.80M',
		link: 'Inspect outflow',
		linkHref: '#discretionary-capex',
		postScenario: '₹1.76M',
	},
	{
		name: 'Collect Apex Retail invoice',
		impact: '+₹620K',
		detail: '12 days overdue → On standard terms',
		link: 'View receivable',
		linkHref: '/receivables',
		postScenario: '₹2.20M',
		recommended: true,
	},
];

function Arrow() {
	return (
		<svg viewBox="0 0 18 18" className="size-4" aria-hidden="true">
			<path
				d="M3 9h11M10 5l4 4-4 4"
				fill="none"
				stroke="currentColor"
				strokeLinecap="round"
				strokeLinejoin="round"
				strokeWidth="1.4"
			/>
		</svg>
	);
}

function MitigationDetails({ option }: { option: MitigationOption }) {
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
						<Arrow />
					</a>
				</div>

				<div className="shrink-0 text-left sm:min-w-36 sm:pt-1">
					<p className="text-sm tabular-nums text-ink">
						{option.postScenario}{' '}
						<span className="text-text-muted">after scenario</span>
					</p>
					<span className="mt-3 inline-flex rounded-full bg-primary-soft px-2.5 py-1 text-xs font-medium text-primary">
						Above buffer
					</span>
				</div>
			</div>
		</div>
	);
}

function MitigationOptionBlock({ option }: { option: MitigationOption }) {
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

function DesktopMitigationSpectrum() {
	return (
		<div
			className="hidden lg:block"
			aria-label="Mitigation options by cash impact"
		>
			<div className="grid grid-cols-[6.5rem_minmax(0,1fr)_6.5rem] items-center">
				<span className="text-xs text-text-muted">Lower impact</span>
				<div className="relative h-14">
					<div className="absolute inset-x-0 top-9 h-px bg-text-muted/45" />
					{mitigationOptions.map((option, index) => (
						<div
							key={option.name}
							className="absolute top-0 -translate-x-1/2 text-center"
							style={{ left: `${index * 33.3333 + 16.6667}%` }}
						>
							<p className="font-serif text-lg text-primary">{option.impact}</p>
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
				<div className="col-start-2 grid grid-cols-3">
					{mitigationOptions.map((option) => (
						<MitigationOptionBlock key={option.name} option={option} />
					))}
				</div>
			</div>
		</div>
	);
}

function MobileMitigationSpectrum() {
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
					{mitigationOptions.map((option) => (
						<div
							key={option.name}
							className="grid grid-cols-[4.5rem_minmax(0,1fr)] items-center gap-x-2"
						>
							<div className="relative -left-3 z-10 flex flex-col items-center gap-1 text-center">
								<span className="font-serif text-base text-primary">
									{option.impact}
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

function CashPosition() {
	return (
		<section className="mt-12 sm:mt-14" aria-labelledby="cash-position-title">
			<p
				id="cash-position-title"
				className="text-xs font-semibold uppercase tracking-[0.14em] text-primary"
			>
				Cash position after this draft
			</p>
			<div className="mt-5 grid gap-7 lg:grid-cols-[minmax(0,1fr)_14rem] lg:items-center lg:gap-14">
				<div>
					<div className="relative pt-[4.25rem]">
						<div className="absolute inset-x-0 top-0 h-14">
							<div className="absolute left-0 top-0">
								<p className="text-xs text-text-muted">Baseline</p>
								<p className="mt-1 font-serif text-base tabular-nums text-ink sm:text-2xl">
									₹1.58M
								</p>
							</div>
							<div className="absolute left-[39%] top-0 -translate-x-1/2 text-center">
								<p className="text-xs text-simulation">Operating buffer</p>
								<p className="mt-1 font-serif text-base tabular-nums text-simulation sm:text-2xl">
									₹1.60M
								</p>
							</div>
							<div className="absolute right-0 top-0 text-right">
								<p className="text-xs text-text-muted">Draft scenario</p>
								<p className="mt-1 font-serif text-base tabular-nums text-ink sm:text-2xl">
									₹2.20M
								</p>
							</div>
						</div>
						<div
							className="relative mt-4 h-2 rounded-full bg-border"
							role="img"
							aria-label="Cash position moves from a baseline of 1.58 million rupees past the 1.60 million rupee operating buffer to a draft scenario of 2.20 million rupees"
						>
							<span className="absolute inset-y-0 left-[39%] right-0 rounded-full bg-primary" />
							<span className="absolute left-[36%] top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-text-muted" />
							<span className="absolute left-[39%] top-1/2 h-6 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-simulation" />
							<span className="absolute right-0 top-1/2 size-4 -translate-y-1/2 translate-x-1/2 rounded-full border-2 border-surface bg-primary" />
						</div>

						<div className="mt-8 flex flex-wrap justify-start gap-x-3 gap-y-2 text-xs text-text-muted sm:justify-center sm:gap-x-10">
							<span className="inline-flex items-center gap-2">
								<span className="size-2.5 rounded-full bg-text-muted/50" />
								Baseline
							</span>
							<span className="inline-flex items-center gap-2">
								<span className="size-2.5 rounded-full bg-simulation" />
								Operating buffer
							</span>
							<span className="inline-flex items-center gap-2">
								<span className="size-2.5 rounded-full bg-primary" />
								Draft scenario
							</span>
						</div>
					</div>
				</div>

				<div className="text-center lg:ml-4 lg:text-left">
					<p className="font-serif text-2xl tabular-nums text-primary sm:text-4xl">
						+₹620K
					</p>
					<p className="mt-1 text-sm text-text-muted">
						improvement vs baseline
					</p>
				</div>
			</div>
		</section>
	);
}

function PlanningPage() {
	return (
		<PageLayout title="Planning">
			<header>
				<p className="text-xs font-semibold uppercase tracking-widest text-primary">
					Planning
				</p>
				<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
					Planning
				</h1>
				<p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted sm:text-lg">
					Turn modeled signals into bounded next steps without committing a
					financial action.
				</p>
			</header>

			<section
				className="mt-10 grid gap-5 lg:grid-cols-2"
				aria-label="Planning recommendations"
			>
				<article className="rounded-card border border-primary/20 bg-primary-soft/35 p-5 sm:p-6">
					<span className="inline-flex rounded-control border border-primary/20 bg-primary-soft px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-primary">
						Recommended next step
					</span>
					<p className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
						Draft recommendation
					</p>
					<h2 className="mt-2 max-w-xl font-serif text-xl leading-tight text-ink sm:text-2xl">
						Bring Apex Retail back to standard terms
					</h2>
					<p className="mt-3 max-w-xl text-sm leading-relaxed text-text-muted">
						Recovering the highest-impact customer balance would move the
						baseline toward the operating buffer.
					</p>
					<a
						href="/receivables"
						className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary no-underline hover:underline"
					>
						View affected customer
						<Arrow />
					</a>
				</article>

				<article className="rounded-card border border-simulation/20 bg-[#fbf8fc] p-5 sm:p-6">
					<span className="inline-flex rounded-control border border-simulation/20 bg-[#f2edf1] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-simulation">
						Draft scenario
					</span>
					<h2 className="mt-4 font-serif text-xl leading-tight text-ink sm:text-2xl">
						Apex Retail collection timing
					</h2>
					<div className="mt-4 grid gap-5 lg:grid-cols-[minmax(0,1fr)_12rem] lg:items-center lg:gap-6">
						<div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-start gap-3 sm:gap-5">
							<div className="min-w-0">
								<p className="text-xs text-text-muted">Current</p>
								<p className="mt-1 font-serif text-sm leading-tight text-ink lg:text-xl">
									12 days overdue
								</p>
							</div>
							<span
								className="mt-5 pb-0.5 text-xl text-simulation"
								aria-hidden="true"
							>
								→
							</span>
							<div className="min-w-0">
								<p className="text-xs text-text-muted">Proposed</p>
								<p className="mt-1 font-serif text-sm leading-tight text-ink lg:text-xl">
									On standard terms
								</p>
							</div>
						</div>
						<div className="flex flex-col gap-3 border-t border-border/80 pt-4 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
							<Button variant="soft" size="sm" className="w-full lg:w-auto">
								Adjust draft
							</Button>
							<p className="text-sm leading-relaxed text-text-muted">
								No accounting action has been committed.
							</p>
						</div>
					</div>
				</article>
			</section>

			<CashPosition />

			<section
				id="mitigation-options"
				className="mt-12 sm:mt-14"
				aria-labelledby="mitigation-options-title"
			>
				<p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
					Mitigation options
				</p>
				<p
					id="mitigation-options-title"
					className="mt-2 font-serif text-lg leading-tight text-ink sm:text-xl"
				>
					Cash impact spectrum
				</p>
				<div className="mt-10 lg:mt-6">
					<DesktopMitigationSpectrum />
					<MobileMitigationSpectrum />
				</div>
			</section>
		</PageLayout>
	);
}

export default PlanningPage;
