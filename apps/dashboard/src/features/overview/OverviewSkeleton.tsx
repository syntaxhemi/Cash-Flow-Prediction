import { Skeleton, SkeletonText } from '@/components/ui/Skeleton';

/** Renders the Overview placeholders while enterprise data is loading. */
function OverviewSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading overview data">
			<div className="mb-10 flex items-center gap-5">
				<SkeletonText className="h-4 w-40" />
				<SkeletonText className="h-4 w-36" />
				<SkeletonText className="h-4 w-24" />
			</div>
			<section className="flex flex-col gap-10 lg:flex-row lg:items-center lg:gap-20">
				<div className="w-full lg:max-w-xl">
					<SkeletonText className="h-3 w-48" />
					<div className="mt-5 flex items-center gap-4">
						<Skeleton className="h-14 w-48 sm:h-16 sm:w-64" />
						<Skeleton className="h-7 w-24 rounded-full" />
					</div>
					<SkeletonText className="mt-4 h-5 w-72 max-w-full" />
				</div>
				<Skeleton className="h-16 w-full max-w-xl" />
			</section>
			<section className="mt-12 sm:mt-20">
				<SkeletonText className="h-6 w-48" />
				<SkeletonText className="mt-2 h-4 w-72" />
				<Skeleton className="mt-8 h-56 w-full rounded-card sm:h-72" />
			</section>
			<div className="mt-12 grid gap-16 sm:mt-20 lg:grid-cols-3 lg:gap-12">
				<Skeleton className="h-44 w-full" />
				<Skeleton className="h-44 w-full lg:col-span-2" />
			</div>
		</div>
	);
}

export default OverviewSkeleton;
