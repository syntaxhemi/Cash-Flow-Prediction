import { Skeleton, SkeletonText } from '@/components/ui/Skeleton';

function ForecastChartSkeleton() {
	return (
		<div className="w-full" aria-hidden="true">
			<Skeleton className="aspect-[360/300] w-full rounded-card sm:aspect-[1000/360]" />
			<SkeletonText className="mt-5 h-3 w-48" />
		</div>
	);
}

function ForecastReadoutSkeleton() {
	return (
		<aside className="mt-12 lg:mt-0 lg:self-stretch lg:border-l lg:border-border lg:pl-12">
			<SkeletonText className="h-3 w-28" />
			<Skeleton className="mt-5 h-20 w-full max-w-sm" />
			<Skeleton className="mt-5 h-16 w-full max-w-sm" />
			<SkeletonText className="mt-6 h-4 w-44" />
		</aside>
	);
}

function CashMovementSkeleton() {
	return (
		<section aria-hidden="true">
			<Skeleton className="h-8 w-44" />
			<div className="mt-6 space-y-4">
				<Skeleton className="h-6 w-full" />
				<Skeleton className="h-6 w-full" />
			</div>
			<Skeleton className="mt-5 h-10 w-full max-w-md" />
		</section>
	);
}

function ForecastImpactSkeleton() {
	return (
		<section aria-hidden="true">
			<Skeleton className="h-8 w-64" />
			<div className="mt-6 grid gap-4 sm:grid-cols-2">
				<Skeleton className="h-36 rounded-card bg-primary-soft sm:col-span-2" />
				<Skeleton className="h-32 rounded-card" />
				<Skeleton className="h-32 rounded-card" />
			</div>
		</section>
	);
}

function ForecastRunsSkeleton() {
	return (
		<section
			className="border-t-0 pt-0 lg:border-t lg:border-border lg:pt-6"
			aria-hidden="true"
		>
			<Skeleton className="h-24 w-full lg:h-8" />
		</section>
	);
}

/** Renders the Forecast page content placeholders while its first result loads. */
function ForecastSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading forecast data">
			<section className="mt-16 lg:mt-24" aria-hidden="true">
				<div className="lg:grid lg:grid-cols-[minmax(0,2.2fr)_minmax(20rem,1fr)] lg:items-start">
					<ForecastChartSkeleton />
					<ForecastReadoutSkeleton />
				</div>
			</section>

			<div className="mt-20 grid gap-16 lg:mt-24 lg:grid-cols-2 lg:gap-20">
				<CashMovementSkeleton />
				<ForecastImpactSkeleton />
			</div>

			<div className="mt-16 lg:mt-20">
				<ForecastRunsSkeleton />
			</div>
		</div>
	);
}

export default ForecastSkeleton;
