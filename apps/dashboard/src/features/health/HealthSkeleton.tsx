import { Skeleton, SkeletonText } from '@/components/ui/Skeleton';

function HealthStatsSkeleton() {
	return (
		<section
			className="mt-14 flex flex-col gap-8 sm:mt-16 sm:grid sm:grid-cols-4 sm:items-center sm:gap-4 lg:gap-8"
			aria-hidden="true"
		>
			{[0, 1, 2, 3].map((index) => (
				<div key={index}>
					<SkeletonText className="h-3 w-24" />
					<Skeleton className="mt-2 h-9 w-32" />
				</div>
			))}
		</section>
	);
}

function HealthPositionSkeleton() {
	return (
		<section aria-hidden="true">
			<Skeleton className="h-8 w-48" />
			<SkeletonText className="mt-3 h-4 w-72 max-w-full" />
			<div className="mt-8 space-y-7">
				{[0, 1].map((index) => (
					<div
						key={index}
						className="grid gap-3 xl:grid-cols-[20rem_minmax(0,1fr)] xl:gap-5"
					>
						<SkeletonText className="h-8 w-56" />
						<Skeleton className="h-4 w-full rounded-full sm:h-[18px]" />
					</div>
				))}
			</div>
			<SkeletonText className="mt-6 h-5 w-36 xl:ml-[21.25rem]" />
		</section>
	);
}

function HealthImpactSkeleton() {
	return (
		<section aria-hidden="true">
			<Skeleton className="h-8 w-64" />
			<SkeletonText className="mt-3 h-4 w-72 max-w-full" />
			<div className="mt-6 grid gap-3 sm:grid-cols-2 sm:gap-4">
				<Skeleton className="h-36 rounded-card bg-primary-soft sm:col-span-2" />
			</div>
		</section>
	);
}

/** Renders Health page placeholders sized to match the loaded sections. */
function HealthSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading health data">
			<HealthStatsSkeleton />
			<div className="mt-16 flex flex-col gap-16 sm:mt-20 sm:gap-20 lg:mt-16 lg:flex-row lg:items-start lg:gap-12 xl:gap-16">
				<div className="mt-0 lg:w-1/2">
					<HealthPositionSkeleton />
				</div>
				<div className="mt-0 lg:w-1/2">
					<HealthImpactSkeleton />
				</div>
			</div>
		</div>
	);
}

export default HealthSkeleton;
