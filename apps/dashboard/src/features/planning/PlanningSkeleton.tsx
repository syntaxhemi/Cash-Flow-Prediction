import { Skeleton, SkeletonText } from '@/components/ui/Skeleton';

/** Renders Planning placeholders sized to match the loaded content. */
function PlanningSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading planning data">
			<section className="mt-10 grid gap-5 lg:grid-cols-2" aria-hidden="true">
				<Skeleton className="h-56 rounded-card bg-primary-soft" />
				<Skeleton className="h-56 rounded-card bg-[#fbf8fc]" />
			</section>
			<section className="mt-12 sm:mt-14" aria-hidden="true">
				<SkeletonText className="h-3 w-36" />
				<div className="mt-5 grid gap-7 lg:grid-cols-[minmax(0,1fr)_14rem]">
					<Skeleton className="h-28 w-full rounded-control" />
					<Skeleton className="h-16 w-full rounded-control" />
				</div>
			</section>
			<section className="mt-12 sm:mt-14" aria-hidden="true">
				<SkeletonText className="h-3 w-32" />
				<SkeletonText className="mt-3 h-7 w-56" />
				<div className="mt-10 grid gap-5 lg:grid-cols-3">
					{[0, 1, 2].map((index) => (
						<Skeleton key={index} className="h-36 rounded-control" />
					))}
				</div>
			</section>
		</div>
	);
}

export default PlanningSkeleton;
