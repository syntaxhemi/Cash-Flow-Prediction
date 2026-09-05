import { Skeleton, SkeletonText } from '@/components/ui/Skeleton';

/** Renders Data page placeholders aligned to the loaded page regions. */
function DataSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading data sources">
			<section className="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
				<Skeleton className="h-64 rounded-card" />
				<Skeleton className="h-64 rounded-card" />
			</section>
			<section className="mt-14">
				<SkeletonText className="h-3 w-36" />
				<div className="mt-6 grid grid-cols-4 gap-6">
					{[0, 1, 2, 3].map((index) => (
						<Skeleton key={index} className="h-20 rounded-control" />
					))}
				</div>
			</section>
			<section className="mt-14">
				<SkeletonText className="h-3 w-32" />
				<Skeleton className="mt-5 h-44 rounded-control" />
			</section>
		</div>
	);
}

export default DataSkeleton;
